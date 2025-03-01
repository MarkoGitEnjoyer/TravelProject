from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from main.models import Registration, Trip

@login_required
def guide_dashboard(request):
    if not hasattr(request.user, "guide"):  
        return redirect("/login/")

    guide = request.user.guide  
    trip = guide.trip  
    registrations = Registration.objects.filter(trip=trip)  

    if request.method == "POST":
        registration_id = request.POST.get("registration_id")
        registration = Registration.objects.get(id=registration_id)
        registration.attended = not registration.attended  
        registration.save()

    return render(request, "GuideApp/guide_dashboard.html", {
        "trip": trip,
        "registrations": registrations,
        "guide": guide
    })