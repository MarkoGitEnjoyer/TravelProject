from django.contrib.auth.models import User
from django.db import models

class Guide(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"