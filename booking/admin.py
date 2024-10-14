# booking/admin.py
from django.urls import path
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.contrib import admin
from django.template.response import TemplateResponse
from booking.models import Booking
from drivers.models import Driver, VehicleType

# class FleetAdmin(admin.ModelAdmin):
#     change_list_template = "admin/fleet_dashboard.html"
    
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('analytics/', self.admin_site.admin_view(self.analytics_view), name="fleet-analytics"),
#         ]
#         return custom_urls + urls

#     def analytics_view(self, request):
#         # Analytics logic
#         total_drivers = Driver.objects.count()
#         available_drivers = Driver.objects.filter(is_available=True).count()
#         total_bookings = Booking.objects.count()
#         completed_trips = Booking.objects.filter(status='DELIVERED').count()
#         avg_trip_time = Booking.objects.filter(status='DELIVERED').aggregate(Avg('estimated_time_min'))['estimated_time_min__avg']

#         context = dict(
#             self.admin_site.each_context(request),
#             total_drivers=total_drivers,
#             available_drivers=available_drivers,
#             total_bookings=total_bookings,
#             completed_trips=completed_trips,
#             avg_trip_time=avg_trip_time,
#         )
#         return TemplateResponse(request, "admin/fleet_analytics.html", context)

admin.site.register(Booking)
admin.site.register(VehicleType)
