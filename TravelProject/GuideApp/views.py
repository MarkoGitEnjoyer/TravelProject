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

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def ScanQR(request):
    return render(request, "GuideApp/ScanQR.html")

def process_qr(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            qr_data = data.get("qr_data", "")

            # Split the scanned QR data to get user_id and SecretKey
            data_parts = qr_data.split('|')
            user_id = data_parts[0]
            secret_key = data_parts[1]

            return JsonResponse({"message": f"User ID: {user_id}, Secret Key: {secret_key}"})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
