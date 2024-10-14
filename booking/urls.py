from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_booking, name='create_booking'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('update-status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('', views.check_bookings, name='all_bookings'),
]
