from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from main.models import Registration, Trip
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
import pandas as pd
from .models import Guide
logger = logging.getLogger(__name__)

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





def ScanQR(request,trip_id):
    trip = Trip.objects.get(trip_id=trip_id)  # Fetch the trip using trip_id
    return render(request, "GuideApp/ScanQR.html", {"trip": trip})


@csrf_exempt
@login_required
def trip_attendance(request, guide_id):
    
    # Get the guide
    guide = Guide.objects.get(id=guide_id)
    
    # Get the trip associated with the guide
    trip = guide.trip # Fetch the first (and only) trip for the guide
    
    # If no trip exists for the guide, handle it gracefully
    if not trip:
        return render(request, 'GuideApp/trip_attendance.html', {
            'guide': guide,
            'registrations': [],
            'error': 'No trip found for this guide.',
        })
    
    # Get all registrations for this trip
    registrations = Registration.objects.filter(trip=trip).select_related('trip')
    
    # Pass data to the template
    context = {
        'guide': guide,
        'trip': trip,  # Pass the trip to the template
        'registrations': registrations,
    }
    return render(request, 'GuideApp/trip_attendance.html', context)


   
@csrf_exempt
def process_qr(request, trip_id):
    print(f"\n=== NEW REQUEST ===")
    print(f"Method: {request.method}")
    
    if request.method == "POST":
        try:
            print(f"Raw body: {request.body.decode('utf-8')}")
            
            # Parse JSON data
            data = json.loads(request.body)
            qr_data = data.get("qr_data", "NO_DATA")
            print(f"QR Data: {qr_data}")

            # Validate QR data
            if not qr_data:
                print("! Empty QR data")
                return JsonResponse({"error": "Empty QR data"}, status=400)

            if '|' not in qr_data:
                print(f"! Missing pipe in: {qr_data}")
                return JsonResponse({"error": "Invalid QR format"}, status=400)

            # Split QR data into parts
            data_parts = qr_data.split('|')
            if len(data_parts) != 2:
                print(f"! Invalid parts: {data_parts}")
                return JsonResponse({"error": "Invalid data format"}, status=400)

            user_id, secret_key = data_parts
            print(f"Processing: User={user_id}, Key={secret_key}")

            # Find the registration for the user and trip
            try:
                registration = Registration.objects.get(id_number=user_id, trip_id=trip_id)
            except Registration.DoesNotExist:
                print(f"! Registration not found for User ID: {user_id}, Trip ID: {trip_id}")
                return JsonResponse({"error": "Registration not found"}, status=404)

            # Update the attended field
            registration.attended = True
            registration.save()
            print(f"Updated registration: {registration.id}")

            # Return success response
            return JsonResponse({
                "message": f"User ID: {user_id}, Secret Key: {secret_key}",
                "user_id": user_id,
                "secret_key": secret_key,
                "attended": True
            })

        except json.JSONDecodeError as e:
            print(f"! JSON Error: {str(e)}")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
            
        except Exception as e:
            print(f"! Critical Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    print("! Invalid method")
    return JsonResponse({"error": "Invalid request method"}, status=405)


