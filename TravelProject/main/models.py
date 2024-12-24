from django.core.validators import RegexValidator
from django.db import models

# Create your models here.
class Trip(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.CharField(max_length=200)
    link = models.URLField()
    date = models.DateField()
    time = models.TimeField()
    meeting_point = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Registration(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex='^[0-9]*$', message='Phone number must be numeric')]
    )    
    email = models.EmailField()
    id_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"