from django.contrib import admin
from users.models import User
from booking.models import Booking
from drivers.models import Driver

admin.site.register(User)
admin.site.register(Booking)
admin.site.register(Driver)

# Register your models here.
