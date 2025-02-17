from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from trips.models import Trip, Registration

@login_required
def guide_dashboard(request):
    try:
        guide = request.user.guide
    except AttributeError:
        return redirect('home')
    
    assigned_trips = Trip.objects.filter(guide=guide)
    
    registrations = Registration.objects.filter(trip__in=assigned_trips)
    
    return render(request, 'guides/dashboard.html', {
        'guide': guide,
        'registrations': registrations,
        'trips': assigned_trips
    })