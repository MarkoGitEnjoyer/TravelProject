from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import guide_dashboard

app_name = "GuideApp"

urlpatterns = [
    path("guide_dashboard/", guide_dashboard, name="guide_dashboard"),
    path('ScanQR/<int:trip_id>/',views.ScanQR,name="ScanQR"),
    path('process_qr/<int:trip_id>/', views.process_qr, name='process_qr'),
    path('trip_attendance/', views.trip_attendance, name='trip_attendance')
    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)