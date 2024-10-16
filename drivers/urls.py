from django.urls import path
from drivers import views

urlpatterns = [
    # ... other URL patterns ...
    path('dashboard/stats/', views.dashboard, name='driver_stats'),
    path('update-location/', views.update_location, name='update_location'),
    path('current-booking/', views.get_current_booking, name='current_booking'),
    path('location/<int:driver_id>/', views.driver_location, name='driver_location'),
    path('dashboard/', views.driver_dashboard, name='driver_dashboard'),
]
