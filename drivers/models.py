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

    def __str__(self):
        return f"{self.user.username} - {self.vehicle_type.name}"


class VehicleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    per_km = models.DecimalField(max_digits=10, decimal_places=2)
    per_min = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=1)  # Number of goods/items

    def __str__(self):
        return self.name
