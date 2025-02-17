from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path



urlpatterns = [
    path('dashboard/', views.guide_dashboard, name='guide_dashboard'),
]
urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)