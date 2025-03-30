from django.core.validators import RegexValidator
from django.db import models
from GuideApp.models import Guide  


# Create your models here.

    
class Trip(models.Model):
    trip_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    minimizedDescription = models.TextField(null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='trip_images/') 
    date = models.DateField()
    time = models.TimeField()
    meeting_point = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    equipment_needed = models.TextField(null=True, blank=True)  # New field for equipment needed
    meeting_point_coordinates = models.CharField(max_length=100, null=True, blank=True)  # New field for coordinates

    def __str__(self):
        return self.name

class Registration(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex='^[0-9]*$', message='Phone number must be numeric')]
    )    
    email = models.EmailField()
    notes = models.TextField(blank=True, null=True)  # New notes field replacing id_number
    attended = models.BooleanField(default=False) 
    SecretKey = models.CharField(max_length=12,null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"