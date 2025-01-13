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


def send_custom_email(request, recipient_email, message_string):
    send_mail(
        'Thank you for ordering ',  # Replace with your desired subject
        message_string,  # The message string passed as a parameter
        'John Doe <john.doe@example.com>',  # The sender's name and email
        [recipient_email],  # The recipient's email address passed as a parameter
        fail_silently=False,
    )
    return HttpResponse("Email sent successfully!")


def trip_info(request, trip_id):
    trip = get_object_or_404(Trip, trip_id=trip_id)
    return render(request, "main/trip_info.html", {"trip": trip})

def home(request):
    trips = Trip.objects.all() 
    return render(request, "main/trip_list.html",{"trips": trips})

def Checkout(request):
    return render(request, "main/Checkout.html")
def trip_list(request):
    trips = Trip.objects.all() 
    return render(request, "main/trip_list.html",{"trips": trips})

def registration(request, trip_id):
    trip = get_object_or_404(Trip, trip_id=trip_id)
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)  
            registration.trip = trip  
            registration.save()  
            return redirect(reverse("confirmation", kwargs={"registration_id": registration.id}))
    else:
        form = RegistrationForm()
    return render(request, "main/registration.html", {"trip": trip, "form": form})


def confirmation(request, registration_id):
    registration = Registration.objects.get(id=registration_id)
    return render(request, "main/confirmation.html", {"registration": registration})