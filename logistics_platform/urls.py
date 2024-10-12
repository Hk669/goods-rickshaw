from django.contrib import admin
from django.urls import path, include
from .views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('users/', include('users.urls')),
    path('bookings/', include('booking.urls')),
    path('drivers/', include('drivers.urls')),
]
