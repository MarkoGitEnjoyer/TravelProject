from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager,CustomUser
from django.conf import settings  
from django.apps import apps


class Guide(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guide')
    phone = models.CharField(max_length=15)
    trip = models.ForeignKey('main.Trip', on_delete=models.SET_NULL, null=True, blank=True, related_name='guides')  


    def __str__(self):
        return self.user.email  