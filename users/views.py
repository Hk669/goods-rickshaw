from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        location = request.POST.get('location')

        user = User.objects.create_user(username=username, password=password, role=role, location=location)
        login(request, user)
        return redirect('home')

    return render(request, 'register.html')
