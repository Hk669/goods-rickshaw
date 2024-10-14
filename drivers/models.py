from django.db import models
from users.models import User
from django.contrib.gis.db import models as gis_models

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey('VehicleType', on_delete=models.CASCADE)
    current_location = gis_models.PointField(geography=True, null=True, blank=True)
    license_plate = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    total_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_completed_bookings = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            gis_models.Index(fields=['current_location']),
        ]

    def __str__(self):
        return f"{self.user.phone_number} - {self.vehicle_type.name}"

    def update_earnings_and_bookings(self):
        completed_bookings = self.booking_set.filter(status='DELIVERED')
        self.total_completed_bookings = completed_bookings.count()
        self.total_earnings = sum(booking.price for booking in completed_bookings)
        self.save()

class VehicleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    per_km = models.DecimalField(max_digits=10, decimal_places=2)
    per_min = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=1)  # Number of goods/items

    def __str__(self):
        return self.name
