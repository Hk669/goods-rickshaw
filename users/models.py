from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('driver', 'Driver'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    location = models.CharField(max_length=255, null=True, blank=True)  # String for address
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    