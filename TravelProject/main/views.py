from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Registration, Trip
from .forms import RegistrationForm
from io import BytesIO
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import openpyxl
import qrcode
import logging
import random
from GuideApp.models import Guide



logger = logging.getLogger(__name__)

def update_registration(request, id):
    registration = get_object_or_404(Registration, id=id)
    if request.method == "POST":
        registration.first_name = request.POST['first_name']
        registration.last_name = request.POST['last_name']
        registration.email = request.POST['email']
        registration.phone = request.POST['phone']
        registration.id_number = request.POST['id_number']
        registration.trip.name = request.POST['trip_name']
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



def send_custom_email(request, recipient_email, first_name, last_name, trip_name, message_string, user_id, SecretKey):
    """
    Sends a custom email with trip details, QR code, and personalized name.

    Args:
        request: The HTTP request object.
        recipient_email (str): Recipient's email address.
        first_name (str): Recipient's first name.
        last_name (str): Recipient's last name.
        trip_name (str): Name of the trip ordered.
        message_string (str): Additional details or a custom message.
        user_id (str): Unique identifier for generating the QR code.
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
    qr.add_data(user_id)
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
    return render(request, "main/trip_info.html", {"trip": trip})

def home(request):
    trips = Trip.objects.all() 
    return render(request, "main/trip_list.html",{"trips": trips})

def Checkout(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    if request.method == "POST":

        send_custom_email(
            request,
            recipient_email=registration.email,
            first_name=registration.first_name,
            last_name=registration.last_name,
            trip_name=registration.trip.name,
            message_string=f" for trip {registration.trip.name}",
            user_id=registration.id_number,
            SecretKey=dehash_number(int(registration.SecretKey)),
        )

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
                return redirect(f"/guide/trip_attendance/{user.id}")
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
    
    ws.append(["#", "First Name", "Last Name", "Email", "Phone","Passport ID", "Trip Name"])
    
    registrations = Registration.objects.all()
    for idx, registration in enumerate(registrations, start=1):
        ws.append([idx, registration.first_name, registration.last_name, registration.email, registration.phone,registration.id_number,registration.trip.name])
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=registrations.xlsx'
    
    wb.save(response)
    return response


def custom_logout(request):
    logout(request)
    return redirect('trip_list')
