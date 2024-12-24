from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("trip_list/", views.trip_list, name="trip_list"),
    path("registration/", views.registration, name="registration"),
    path("confirmation/<int:registration_id>/", views.confirmation, name="confirmation"),
    path("Checkout/", views.Checkout,name="Checkout")
] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)