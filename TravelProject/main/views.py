from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Registration
from .models import Trip
from .forms import RegistrationForm

def home(request):
    return render(request, "main/home.html")

def trip_list(request):
    trips = Trip.objects.all() 
    return render(request, "main/trip_list.html",{"trips": trips})

def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save()
            return redirect(reverse("confirmation", kwargs={"registration_id": registration.id}))
    else:
        form = RegistrationForm()
    return render(request, "main/registration.html", {"form": form})

def confirmation(request, registration_id):
    registration = Registration.objects.get(id=registration_id)
    return render(request, "main/confirmation.html", {"registration": registration})