from django.urls import path
from users import views

urlpatterns = [
    # ... other URL patterns ...
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_user_otp, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('verify-login-otp/', views.verify_login_otp, name='verify_login_otp'),
    path('logout/', views.logout_view, name='logout'),
    # path('update-profile/', views.update_profile, name='update_profile'),  # To be implemented
    # ... other URL patterns ...
]
