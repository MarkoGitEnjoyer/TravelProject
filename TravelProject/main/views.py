from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import Registration
from .models import Trip
from .forms import RegistrationForm

from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMessage
import qrcode
from io import BytesIO


def update_registration(request, id):
    registration = get_object_or_404(Registration, id=id)
    if request.method == "POST":
        registration.first_name = request.POST['first_name']
        registration.last_name = request.POST['last_name']
        registration.email = request.POST['email']
        registration.phone = request.POST['phone']
        registration.save()
        return redirect('spreadsheet')  
    return HttpResponseRedirect('/')

import logging
logger = logging.getLogger(__name__)
def delete_registration(request, id):
    if request.method == "POST":
        logger.debug(f"Deleting registration: {id}")  # Log message
        
        try:
            registration = get_object_or_404(Registration, id=id)
            registration.delete()
        except Exception as e:
            logger.error(f"Failed to delete registration: {e}")  # Log error message    

    return redirect('spreadsheet')



def send_custom_email(request, recipient_email, first_name, last_name, trip_name, message_string, user_id):
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
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(user_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)  

    trip = Trip.objects.get(name=trip_name)

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
        # Update registration details if necessary
        registration.first_name = request.POST.get("first_name")
        registration.last_name = request.POST.get("last_name")
        registration.phone = request.POST.get("phone")
        registration.email = request.POST.get("email")
        registration.id_number = request.POST.get("passport_id")
        registration.save()

        # Send the email
        send_custom_email(
            request,
            recipient_email=registration.email,
            first_name=registration.first_name,
            last_name=registration.last_name,
            trip_name=registration.trip.name,
            message_string=f" for trip {registration.trip.name}",
            user_id=registration.id_number
        )

        return redirect(reverse("confirmation", kwargs={"registration_id": registration.id}))

    return render(request, "main/Checkout.html", {'registration': registration})


def trip_list(request):
    trips = Trip.objects.all() 
    return render(request, "main/trip_list.html",{"trips": trips})

def spreadsheet(request):
    registrations = Registration.objects.all() 
    return  render(request, "main/spreadsheet.html",{"registrations": registrations})
def contact_us(request):
    return render(request, "main/contact_us.html")


def registration(request, trip_id):
    trip = get_object_or_404(Trip, trip_id=trip_id)
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)  
            registration.trip = trip  
            registration.save()  
            return redirect(reverse("Checkout", kwargs={"registration_id": registration.id}))
    else:
        form = RegistrationForm()
    return render(request, "main/registration.html", {"trip": trip, "form": form})


def confirmation(request, registration_id):
    registration = Registration.objects.get(id=registration_id)
    return render(request, "main/confirmation.html", {"registration": registration})