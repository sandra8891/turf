from django.db import models
from datetime import time
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Turf(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    images = models.ImageField(upload_to='turf_images/')
    sport_types = models.CharField(max_length=100, choices=[('Football', 'Football'), ('Cricket', 'Cricket')])
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return self.name


class Slot(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.turf.name} - {self.date} {self.start_time}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey('Slot', on_delete=models.CASCADE)
    address = models.CharField(max_length=255, default="Not provided")
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    sport = models.CharField(max_length=100)
    players = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)  # Set a default
    
    def __str__(self):
        return f"Booking for {self.slot} by {self.user.username}"
    
    
    
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"