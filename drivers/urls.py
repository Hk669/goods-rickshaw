from django.urls import path
from drivers import views

urlpatterns = [
    # ... other URL patterns ...
    path('dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('update-location/', views.update_location, name='update_location'),
]
