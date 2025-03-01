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

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
logger = logging.getLogger(__name__)
@csrf_exempt
def process_qr(request):
    print(f"\n=== NEW REQUEST ===")
    print(f"Method: {request.method}")
    
    if request.method == "POST":
        try:
            print(f"Raw body: {request.body.decode('utf-8')}")
            
            data = json.loads(request.body)
            qr_data = data.get("qr_data", "NO_DATA")
            print(f"QR Data: {qr_data}")

            if not qr_data:
                print("! Empty QR data")
                return JsonResponse({"error": "Empty QR data"}, status=400)

            if '|' not in qr_data:
                print(f"! Missing pipe in: {qr_data}")
                return JsonResponse({"error": "Invalid QR format"}, status=400)

            data_parts = qr_data.split('|')
            if len(data_parts) != 2:
                print(f"! Invalid parts: {data_parts}")
                return JsonResponse({"error": "Invalid data format"}, status=400)

            user_id, secret_key = data_parts
            print(f"Processing: User={user_id}, Key={secret_key}")
            
            return JsonResponse({
                "message": f"User ID: {user_id}, Secret Key: {secret_key}",
                "user_id": user_id,
                "secret_key": secret_key
            })

        except json.JSONDecodeError as e:
            print(f"! JSON Error: {str(e)}")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
            
        except Exception as e:
            print(f"! Critical Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    print("! Invalid method")
    return JsonResponse({"error": "Invalid request method"}, status=405)
