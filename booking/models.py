from django.db import models
from users.models import User
from drivers.models import Driver

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('en_route', 'En Route'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name='driver_bookings')
    pickup_address = models.CharField(max_length=255)
    dropoff_address = models.CharField(max_length=255)
    # pickup_location = gis_models.PointField(geography=True)
    # dropoff_location = gis_models.PointField(geography=True)
    pickup_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    dropoff_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    dropoff_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)  # Automatically calculated
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # In kilometers
    estimated_time = models.CharField(max_length=50, null=True, blank=True)  # Duration as string (e.g., "25 mins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.id} - {self.status} by {self.customer.username}"
