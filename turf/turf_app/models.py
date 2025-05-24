# models.py
from django.db import models
from datetime import time
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class PaymentStatus:
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'

class Turf(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    sport_types = models.CharField(max_length=100, choices=[('Football', 'Football'), ('Cricket', 'Cricket')])
    open_time = models.TimeField()
    close_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class TurfImage(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='turf_images/')

    def __str__(self):
        return f"Image for {self.turf.name}"



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
    created_at = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Added total_amount
    status = models.CharField(
        max_length=50,
        default=PaymentStatus.PENDING,
        choices=[
            (PaymentStatus.PENDING, 'Pending'),
            (PaymentStatus.COMPLETED, 'Completed'),
            (PaymentStatus.CANCELLED, 'Cancelled'),
        ]
    )
    provider_order_id = models.CharField(_("Order ID"), max_length=40, blank=True, null=True)
    payment_id = models.CharField(_("Payment ID"), max_length=36, blank=True, null=True)
    signature_id = models.CharField(_("Signature ID"), max_length=128, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Automatically set total_amount based on turf price
        if not self.total_amount:
            self.total_amount = self.slot.turf.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for {self.slot} by {self.user.username}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"