from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import DriverLocationForm
from .models import Driver
from django.contrib.gis.geos import Point

@login_required
def driver_dashboard(request):
    # Render the driver dashboard with a map
    return render(request, 'drivers/dashboard.html')

@login_required
def update_location(request):
    if request.method == 'POST' and request.is_ajax():
        form = DriverLocationForm(request.POST)
        if form.is_valid():
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            try:
                driver = Driver.objects.get(user=request.user)
                driver.current_location = Point(longitude, latitude)
                driver.save()
                return JsonResponse({'status': 'success'})
            except Driver.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Driver profile not found.'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)
