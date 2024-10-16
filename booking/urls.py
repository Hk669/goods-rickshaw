from django.urls import path
from .views import create_booking, booking_detail, update_booking_status, check_bookings, accept_booking, accept_booking_redirect, cancel_booking

urlpatterns = [
    path('create/', create_booking, name='create_booking'),
    path('<int:booking_id>/', booking_detail, name='booking_detail'),
    path('update-status/<int:booking_id>/', update_booking_status, name='update_booking_status'),
    path('', check_bookings, name='all_bookings'),
    path('accept_booking/', accept_booking, name='accept_booking'),
    path('<int:booking_id>/accept/', accept_booking_redirect, name='accept_booking_redirect'),
    path('bookings/<int:booking_id>/cancel/', cancel_booking, name='cancel_booking'),
]
