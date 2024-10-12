from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_booking, name='create-booking'),
    # path('<int:pk>/', views.booking_detail, name='booking_detail'),
]
