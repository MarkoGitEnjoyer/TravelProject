from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Registration, Trip,Coupon
from .forms import RegistrationForm,PaymentForm
from io import BytesIO
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import openpyxl
import qrcode
import logging
import random
from decimal import Decimal
from .utils.vonage_sms import VonageSMSService
from django.conf import settings
from GuideApp.models import Guide
from vonage import Auth, Vonage
from vonage_sms import SmsMessage, SmsResponse
from django.contrib import messages
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

def update_registration(request, id):
    registration = get_object_or_404(Registration, id=id)
    if request.method == "POST":
        registration.first_name = request.POST['first_name']
        registration.last_name = request.POST['last_name']
        registration.email = request.POST['email']
        registration.phone = request.POST['phone']
        registration.notes = request.POST['notes']  # Changed from id_number to notes
        registration.save()
        return redirect('spreadsheet')  
    return HttpResponseRedirect('/')

def delete_registration(request, id):
    if request.method == "POST":
        logger.debug(f"Deleting registration: {id}")  
        
        try:
            registration = get_object_or_404(Registration, id=id)
            registration.delete()
        except Exception as e:
            logger.error(f"Failed to delete registration: {e}")  
    return redirect('spreadsheet')


def generate_secret_key():
    return random.randint(1, 999999)

SECRET_KEY = 12345  # Any large prime number
SHIFT = 6789        # A shift value for extra obfuscation

def hash_number(number):
    """Hashes a number using a reversible mathematical operation."""
    return (number * SECRET_KEY) + SHIFT

def dehash_number(hashed_value):
    """Reverses the hash function to get the original number."""
    return (hashed_value - SHIFT) // SECRET_KEY



def send_custom_email(request, recipient_email, first_name, last_name, trip_name, message_string, user_phone, SecretKey):
    """
    Sends a custom email with trip details, QR code, and personalized name.

    Args:
        request: The HTTP request object.
        recipient_email (str): Recipient's email address.
        first_name (str): Recipient's first name.
        last_name (str): Recipient's last name.
        trip_name (str): Name of the trip ordered.
        message_string (str): Additional details or a custom message.
        user_phone (str): Phone number for generating the QR code.
        SecretKey (str): Secret key for generating the QR code.
    """
    import qrcode
    from io import BytesIO
    from django.core.mail import EmailMessage
    from django.http import HttpResponse
    from .models import Trip  # Ensure Trip model is imported

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(user_phone)  # Use phone instead of id_number
    qr.add_data('|')
    qr.add_data(SecretKey)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)

    # Fetch trip details
    trip = Trip.objects.get(name=trip_name)

    # Prepare email content
    subject = f"Trip Confirmation for {trip_name}"
    body = f"""
    Hi {first_name} {last_name},

    Thank you for booking your trip with us! Here are the details:

    Trip Name: {trip_name}
    Date: {trip.date}
    Time: {trip.time}
    Meeting Point: {trip.meeting_point}
    Additional Information: {message_string}

    Please find your trip ticket attached as a QR code. You can present this code upon arrival.

    If you have any questions, feel free to reach out to us.

    Best regards,
    Your Travel Team
    """

    # Create and send email
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email='My trips <saitama100new@gmail.com>',
        to=[recipient_email],
    )
    email.attach('Trip_Ticket.png', img_io.getvalue(), 'image/png')

    try:
        email.send(fail_silently=False)
        return HttpResponse("Email with QR code sent successfully!")
    except Exception as e:
        return HttpResponse(f"Failed to send email: {e}", status=500)
        

def trip_info(request, trip_id):
    trip = get_object_or_404(Trip, trip_id=trip_id)
    gallery_images = trip.gallery_images.all()
    context = {
        'trip': trip,
        'gallery_images': gallery_images,
        'active_page': 'trips',
        
    }
    return render(request, "main/trip_info.html", context)

def home(request):
    trips = Trip.objects.all() 
    return render(request, "main/trip_list.html",{"trips": trips})

@require_POST # Ensure this view only accepts POST requests
def validate_coupon_view(request):
    coupon_code = request.POST.get('coupon_code', '').strip()
    registration_id = request.POST.get('registration_id')

    data = { # Default invalid response structure
        'valid': False,
        'message': 'Please enter a coupon code.',
        'discount_amount': '0.00',
        'final_total': '0.00', # Will be updated if valid
        'applied_code': '',
    }

    if not registration_id:
        data['message'] = 'Missing registration context.'
        return JsonResponse(data, status=400) # Bad request

    if not coupon_code:
        # Message already set in default structure
        return JsonResponse(data)

    try:
        registration = get_object_or_404(Registration, pk=registration_id)
        # Calculate base price details for this registration
        # Ensure trip cost is valid
        if registration.trip.cost is None:
             raise ValueError("Trip cost is undefined.")

        # Need num_travelers - get from session? Or assume 1 if not stored? BEST to get from session.
        pending_details = request.session.get('pending_payment_details')
        if not pending_details or pending_details.get('registration_id') != int(registration_id):
             raise ValueError("Pending details not found in session.")

        num_travelers = pending_details.get('num_travelers', 1)
        cost_per_ticket = registration.trip.cost
        subtotal = cost_per_ticket * num_travelers
        tax_rate = Decimal('0.00') # Example tax rate - use your actual logic
        tax = (subtotal * tax_rate).quantize(Decimal("0.01")) # Tax based on subtotal
        original_total = subtotal + tax

        # Try to find the coupon
        coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)

        # --- Coupon Validation Logic ---
        # Add more checks if needed (e.g., expiry date, usage limit, applicable trips)

        # Calculate discount (assuming percentage)
        discount_percentage = coupon.discount_percentage if coupon.discount_percentage is not None else Decimal('0.00')
        discount_amount = (subtotal * (discount_percentage / Decimal('100'))).quantize(Decimal("0.01"))

        # Calculate final total (apply discount BEFORE tax? Or after? Affects final price!)
        # Example: Discount applied before tax
        price_after_discount = subtotal - discount_amount
        final_tax_calculated = (price_after_discount * tax_rate).quantize(Decimal("0.01")) # Recalculate tax if needed
        final_total_calculated = price_after_discount + final_tax_calculated

        # If discount applied after tax:
        # final_total_calculated = original_total - discount_amount

        if final_total_calculated < 0: final_total_calculated = Decimal('0.00')

        # Update response data for valid coupon
        data['valid'] = True
        data['message'] = f"Coupon '{coupon.code}' applied!"
        data['discount_amount'] = f"{discount_amount:.2f}"
        data['final_total'] = f"{final_total_calculated:.2f}"
        data['applied_code'] = coupon.code

    except Registration.DoesNotExist:
         data['message'] = "Booking context not found."
         return JsonResponse(data, status=404)
    except Coupon.DoesNotExist:
        data['message'] = f"Coupon code '{coupon_code}' not found or is inactive."
        data['final_total'] = f"{original_total:.2f}" # Return original total if coupon invalid
    except ValueError as ve: # Handle missing cost or session data
        logger.warning(f"Value error validating coupon {coupon_code} for registration {registration_id}: {ve}")
        data['message'] = "Could not calculate price for coupon application."
        # Optionally return original total if calculation base fails
        try: data['final_total'] = f"{original_total:.2f}"
        except NameError: pass # original_total might not be set if cost was None
    except Exception as e:
        logger.error(f"Error validating coupon {coupon_code} for registration {registration_id}: {e}", exc_info=True)
        data['message'] = "An error occurred while validating the coupon."
        # Optionally return original total on general error
        try: data['final_total'] = f"{original_total:.2f}"
        except NameError: pass

    return JsonResponse(data)
def booking_view(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)

    if request.method == 'POST':
        # 1. Get data from request.POST
        num_travelers_str = request.POST.get('num_travelers')
        full_name_input = request.POST.get('full_name', '').strip()
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        # Map form field 'requests' to model field 'notes'
        notes_text = request.POST.get('requests', '')

        # 2. Split Full Name
        first_name = ""
        last_name = ""
        if full_name_input:
            name_parts = full_name_input.split()
            if len(name_parts) >= 1: first_name = name_parts[0]
            if len(name_parts) > 1: last_name = " ".join(name_parts[1:])

        # 3. Validation
        errors = {}
        num_travelers = 0
        try:
            num_travelers = int(num_travelers_str)
            if num_travelers < 1:
                 errors['num_travelers'] = "Please enter a valid number of travelers (at least 1)."
        except (ValueError, TypeError):
            errors['num_travelers'] = "Please enter a valid number for travelers."

        if not first_name: errors['full_name'] = "Please enter at least a first name."
        # Optional: Add validation if last_name is required by your model
        # if not last_name: errors['full_name'] = "Last name is required." # Check model constraints

        if not email: errors['email'] = "Email is required." # Add proper email format validation
        # You might rely on model's RegexValidator for phone or add view validation
        # if phone and not re.match(r'^[0-9]*$', phone): errors['phone'] = "Phone number must be numeric."

        if errors:
            # Re-render form with errors
            messages.error(request, "Please correct the errors below.")
            context = {
                'trip': trip,
                'active_page': 'trips',
                'errors': errors,
                'form_data': request.POST
            }
            return render(request, 'booking.html', context)

        # 4. If validation passed
        try:
            # Calculate cost (needed for payment, even if not saved on Registration model)
            if trip.cost is None:
                # Handle case where trip cost isn't set
                logger.error(f"Trip {trip.id} ('{trip.name}') cost is not defined.")
                messages.error(request, "Sorry, the cost for this trip is not available at the moment.")
                context = {'trip': trip, 'active_page': 'trips', 'form_data': request.POST}
                return render(request, 'booking.html', context)

            total_cost_calculated = trip.cost * num_travelers
            sec = generate_secret_key()
            sec = hash_number(sec)
            # 5. === Create Registration Record ===
            # Uses the imported Registration model
            new_registration = Registration.objects.create(
                trip=trip,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                notes=notes_text,
                SecretKey = sec
                
            )
            new_registration.save()
            registration_id_for_payment = new_registration.id

            # 6. Store details needed for payment page in SESSION
            # Because Registration model doesn't store num_travelers or total_cost
            request.session['pending_payment_details'] = {
                'registration_id': registration_id_for_payment,
                'num_travelers': num_travelers,
                'total_cost': float(total_cost_calculated) # Use float for session compatibility
            }
            logger.info(f"Stored pending payment details in session for Registration ID: {registration_id_for_payment}")


            # 7. Redirect to Payment Page
            payment_url = reverse('pay_trip', kwargs={'booking_id': registration_id_for_payment})

            logger.info(f"Registration {registration_id_for_payment} created. Redirecting to payment: {payment_url}")
            return redirect(payment_url)

        except Exception as e:
             # Handle potential errors during cost calculation or DB save
             logger.error(f"Error processing registration for trip {trip_id}: {e}", exc_info=True)
             messages.error(request, "An unexpected error occurred while processing your registration. Please try again.")
             context = {
                'trip': trip,
                'active_page': 'trips',
                'errors': {'general': 'Could not process registration.'},
                'form_data': request.POST
             }
             return render(request, 'main/booking.html', context)

    # --- GET Request handling ---
    else:
        # Clear any previous pending payment details from session on fresh GET request
        request.session.pop('pending_payment_details', None)
        context = {
            'trip': trip,
            'active_page': 'trips',
            'errors': {},
            'form_data': {} # Empty form data for GET
        }
        return render(request, 'main/booking.html', context)

def payment_view(request, booking_id):
    registration = get_object_or_404(Registration, id=booking_id)
    original_total = registration.trip.cost
    # Ensure original_total is Decimal
    if not isinstance(original_total, Decimal):
        try:
            original_total = Decimal(original_total)
        except InvalidOperation:
            messages.error(request, "Invalid trip cost.")
            # Redirect back or handle error appropriately
            return redirect('trip_list') # Redirect to a safe page

    subtotal = original_total # Base subtotal

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Form fields passed basic validation (required, field type)
            # Access cleaned data: form.cleaned_data['field_name']
            print("DEBUG: Payment form is valid.")

            submitted_coupon_code = form.cleaned_data.get('applied_coupon_code', '').strip()
            final_discount_amount = Decimal('0.00')
            tax_rate = Decimal('0.00') # Set your actual tax rate if applicable

            if submitted_coupon_code:
                print(f"DEBUG: Validating submitted coupon: {submitted_coupon_code}")
                try:
                    coupon = Coupon.objects.get(code__iexact=submitted_coupon_code, is_active=True)
                    # Add other validation checks if needed (e.g., expiry, usage limits)
                    discount_percentage = coupon.discount_percentage if coupon.discount_percentage is not None else Decimal('0.00')
                    final_discount_amount = (original_total * (discount_percentage / Decimal('100'))).quantize(Decimal("0.01"))
                    print(f"DEBUG: Coupon valid. Discount amount: {final_discount_amount}")
                except Coupon.DoesNotExist:
                    messages.error(request, f"Coupon '{submitted_coupon_code}' is no longer valid. Proceeding without discount.")
                    final_discount_amount = Decimal('0.00')
                except Exception as e:
                    print(f"DEBUG: ERROR during coupon validation: {e}")
                    messages.error(request, "An error occurred validating the coupon.")
                    final_discount_amount = Decimal('0.00')

            # --- Recalculate final total ---
            print("DEBUG: Calculating final total...")
            try:
                price_after_discount = original_total - final_discount_amount
                final_tax_calculated = (price_after_discount * tax_rate).quantize(Decimal("0.01"))
                final_total_to_charge = price_after_discount + final_tax_calculated
                if final_total_to_charge < 0: final_total_to_charge = Decimal('0.00')
                print(f"DEBUG: Final total calculated: {final_total_to_charge}")

                # === !!! Placeholder for Secure Payment Gateway Interaction !!! ===
                # 1. Use form.cleaned_data (EXCEPT raw card details)
                # 2. Send final_total_to_charge and other details (billing address, etc.)
                #    to your payment gateway (Stripe, Braintree) using their Python library.
                # 3. Handle the response from the gateway (success or failure).
                
                payment_successful = True # Assume success for now
                # === End Placeholder ===

                if payment_successful:

                    

                    send_custom_email(
                    request,
                    recipient_email=registration.email,
                    first_name=registration.first_name,
                    last_name=registration.last_name,
                    trip_name=registration.trip.name,
                    message_string=f" for trip {registration.trip.name}",
                    user_phone=registration.phone,  # Changed from id_number to phone
                    SecretKey=dehash_number(int(registration.SecretKey)),
                    )

                    
                    # Redirect to confirmation page
                    return redirect(reverse("confirmation", kwargs={"registration_id": registration.id}))
                else:
                    # Payment gateway failed
                    messages.error(request, "Payment failed. Please try again or contact support.")
                    # No redirect, fall through to re-render form with error message

            except InvalidOperation:
                 
                 messages.error(request, "A calculation error occurred.")
                 # No redirect, fall through to re-render form
            except Exception as e:
                 
                 import traceback
                 traceback.print_exc()
                 messages.error(request, "An unexpected error occurred during payment processing.")
                 # No redirect, fall through to re-render form

        # --- Form is NOT valid OR payment failed ---
        # Reaches here if form.is_valid() is False OR if payment_successful was False above
        
        if not form.is_valid(): # Add specific message only if form itself was invalid
             messages.error(request, "Please correct the errors highlighted below.")

        # Need context to re-render template with errors
        context = {
            'registration': registration,
            'form': form, # Pass the bound form (contains errors if invalid)
            # Recalculate totals as they were initially shown
            'num_travelers': 1,
            'subtotal': subtotal,
            'applied_coupon_code': form.cleaned_data.get('applied_coupon_code', '') if form.is_bound else None, # Show code user entered
            'discount_amount': final_discount_amount if form.is_bound and 'final_discount_amount' in locals() else Decimal('0.00'), # Be careful here
            'final_total': final_total_to_charge if form.is_bound and 'final_total_to_charge' in locals() else original_total, # Be careful here
            'errors': form.errors, # Pass form errors explicitly if needed
            'form_data': request.POST if form.is_bound else {}, # Pass POST data back? Careful with sensitive data
            'active_page': 'payment',
        }
        # Return render to show the form again with errors
        return render(request, 'main/payment.html', context) # Provides the needed HttpResponse


    else: # GET Request
        
        # Pre-populate form data if desired
        initial_data = {
            'name': f"{registration.first_name or ''} {registration.last_name or ''}".strip(),
            # Add other initial data from registration if available
            # 'address': registration.address, etc.
        }
        form = PaymentForm(initial=initial_data)
        final_total = original_total # Initial total before any coupons

        context = {
            'registration': registration,
            'form': form, # Pass the unbound form
            'num_travelers': 1, # Adjust if needed
            'subtotal': subtotal,
            'applied_coupon_code': None,
            'discount_amount': Decimal('0.00'),
            'final_total': final_total,
            'errors': {},
            'form_data': {},
            'active_page': 'payment',
        }
        return render(request, 'main/payment.html', context)

def Checkout(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    if request.method == "POST":

        from .utils.vonage_sms import send_trip_confirmation
        
        """
        sms_result = send_trip_confirmation(registration)
        
        # Log result for debugging
        if sms_result.get("success"):
            print(f"SMS sent successfully with message ID: {sms_result.get('message_id')}")
        else:
            print(f"SMS sending failed: {sms_result.get('error')}")
        """
        send_custom_email(
            request,
            recipient_email=registration.email,
            first_name=registration.first_name,
            last_name=registration.last_name,
            trip_name=registration.trip.name,
            message_string=f" for trip {registration.trip.name}",
            user_phone=registration.phone,  # Changed from id_number to phone
            SecretKey=dehash_number(int(registration.SecretKey)),
        )

        
        """
        if sms_result.get('success'):
            logger.info(f"SMS confirmation sent to {registration.phone}")
        else:
            logger.error(f"SMS failed: {sms_result.get('error')}")
        """
        return redirect(reverse("confirmation", kwargs={"registration_id": registration.id}))

    return render(request, "main/Checkout.html", {'registration': registration})

def trip_list(request):
    trips = Trip.objects.all() 
    return render(request, "main/trip_list.html",{"trips": trips})


@login_required
def spreadsheet(request):
    print(f"Is user authenticated? {request.user.is_authenticated}")
    registrations = Registration.objects.all()
    return render(request, "main/spreadsheet.html", {"registrations": registrations})




def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()  
        password = request.POST.get("password", "").strip()

        if not email or not password:
            return render(request, "main/login.html", {"error": "Email and password are required."})

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect("/trip_list/")
            elif hasattr(user, "guide"):
                return redirect(f"/guide/trip_attendance/")
            else:
                return redirect("login")
        else:
            return render(request, "main/login.html", {"error": "Invalid email or password."})

    return render(request, "main/login.html")



def contact_us(request):
    return render(request, "main/contact_us.html")


def registration(request, trip_id):
    trip = get_object_or_404(Trip, trip_id=trip_id)
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)  
            registration.trip = trip  
            sec = generate_secret_key()
            sec = hash_number(sec)
            registration.SecretKey = sec
            registration.save()  
            return redirect(reverse("Checkout", kwargs={"registration_id": registration.id}))
    else:
        form = RegistrationForm()
    return render(request, "main/registration.html", {"trip": trip, "form": form})


def confirmation(request, registration_id):
    registration = Registration.objects.get(id=registration_id)
    return render(request, "main/confirmation.html", {"registration": registration})



def download_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Registrations"
    
    ws.append(["#", "First Name", "Last Name", "Email", "Phone", "Notes", "Trip Name"])
    
    registrations = Registration.objects.all()
    for idx, registration in enumerate(registrations, start=1):
        ws.append([
            idx, 
            registration.first_name, 
            registration.last_name, 
            registration.email, 
            registration.phone,
            registration.notes,  # Changed from id_number to notes
            registration.trip.name
        ])
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=registrations.xlsx'
    
    wb.save(response)
    return response

def custom_logout(request):
    logout(request)
    return redirect('trip_list')
