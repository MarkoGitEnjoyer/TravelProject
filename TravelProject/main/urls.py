from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import send_custom_email
urlpatterns = [
    path("trip_info/<int:trip_id>/", views.trip_info, name="trip_info"),
    path("", views.home, name="home"),
    path("trip_list/", views.trip_list, name="trip_list"),
    path("registration/<int:trip_id>", views.registration, name="registration"),
    path("confirmation/<int:registration_id>/", views.confirmation, name="confirmation"),
    path("Checkout/", views.Checkout,name="Checkout"),
    path(
    'send-email/<str:recipient_email>/<str:first_name>/<str:last_name>/<str:trip_name>/<str:message_string>/<str:user_id>/',
    views.send_custom_email,
    name='send_custom_email'
),



] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)