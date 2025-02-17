from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path


urlpatterns = [
    path("index", views.index, name="index")




] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)