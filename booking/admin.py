from django.contrib import admin
from users.models import User
from booking.models import Booking
from drivers.models import Driver, VehicleType
from django.contrib.gis.admin import OSMGeoAdmin

admin.site.register(User)
admin.site.register(Booking)
admin.site.register(VehicleType)
@admin.register(Driver)
class DriverAdmin(OSMGeoAdmin):
    list_display = ('user', 'vehicle_type', 'current_location', 'license_plate', 'is_available', 'last_updated')
    fields = ('user', 'vehicle_type', 'current_location', 'license_plate', 'is_available')
# Register your models here.
