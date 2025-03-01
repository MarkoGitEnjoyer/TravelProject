from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import guide_dashboard

app_name = "GuideApp"

urlpatterns = [
    path("guide_dashboard/", guide_dashboard, name="guide_dashboard"),
    path('ScanQR/',views.ScanQR,name="ScanQR"),
    path('process_qr/', views.process_qr, name='process_qr'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)