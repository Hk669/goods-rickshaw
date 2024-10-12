from django.db import models
from users.models import User
from drivers.models import Driver, VehicleType
from django.contrib.gis.db import models as gis_models

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('EN_ROUTE', 'En Route'),
        ('PICKED_UP', 'Picked Up'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)
    pickup_location = gis_models.PointField(geography=True)
    dropoff_location = gis_models.PointField(geography=True)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_time_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Add other fields like payment details if necessary

    def __str__(self):
        return f"Booking {self.id} by {self.user.username}"
