from django.db import models
from users.models import User
# from django.contrib.gis.db import models as gis_models

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey('VehicleType', on_delete=models.CASCADE)
    # current_location = gis_models.PointField(geography=True, null=True, blank=True) #GDAL needs to be installed
    license_number = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.vehicle_type}"

class VehicleType(models.Model):
    name = models.CharField(max_length=50)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_minute = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=1)

    def __str__(self):
        return self.name + "capacity: " + self.capacity