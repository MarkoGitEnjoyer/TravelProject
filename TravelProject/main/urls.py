from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import send_custom_email
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("trip_info/<int:trip_id>/", views.trip_info, name="trip_info"),
    path("", views.home, name="home"),
    path("trip_list/", views.trip_list, name="trip_list"),
    path('registrations/edit/<int:id>/', views.update_registration, name='update_registration'),
    path('registrations/delete/<int:id>/', views.delete_registration, name='delete_registration'),
    path("spreadsheet/", views.spreadsheet, name="spreadsheet"),
    path('download_excel/', views.download_excel, name='download_excel'),
    path("contact_us/", views.contact_us, name="contact_us"),
    path("login/", views.admin_login, name="login"),
    path('logout/', views.custom_logout, name='logout'),
    path("registration/<int:trip_id>", views.registration, name="registration"),
    path("confirmation/<int:registration_id>/", views.confirmation, name="confirmation"),
    path("Checkout/<int:registration_id>/", views.Checkout,name="Checkout"),
    path('send-email/<str:recipient_email>/<str:message_string>/<str:user_id>/', views.send_custom_email, name='send_custom_email'),
    path("Checkout/", views.Checkout,name="Checkout"),
    path(
    'send-email/<str:recipient_email>/<str:first_name>/<str:last_name>/<str:trip_name>/<str:message_string>/<str:user_id>/',
    views.send_custom_email,
    name='send_custom_email'
),



] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)