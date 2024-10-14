from django.urls import path
from drivers import views

urlpatterns = [
    # ... other URL patterns ...
    path('dashboard/', views.dashboard, name='driver_dashboard'),
    path('update-location/', views.update_location, name='update_location'),
    path('current-booking/', views.get_current_booking, name='current_booking'),
]
