import os
from decimal import Decimal
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from drivers.models import Driver, VehicleType
from django.core.cache import cache
import json

def find_nearest_drivers(pickup_lat, pickup_lng, vehicle_type_name, max_distance_km=10):
    """
    verifies if the drivers are available and within the max distance(10km) are in cache
    otherwise, it queries the database and caches the result for 5 mins
    """
    cache_key = f"nearest_drivers:{vehicle_type_name}:{pickup_lat}:{pickup_lng}:{max_distance_km}"
    cached_drivers = cache.get(cache_key)

    if cached_drivers:
        # Deserialize cached JSON data
        driver_ids = json.loads(cached_drivers)
        return Driver.objects.filter(id__in=driver_ids)
    
    try:
        vehicle_type = VehicleType.objects.get(name=vehicle_type_name)
    except VehicleType.DoesNotExist:
        return []

    pickup_location = Point(pickup_lng, pickup_lat, srid=4326)

    drivers = Driver.objects.filter(
        vehicle_type=vehicle_type,
        is_available=True,
        current_location__distance_lte=(pickup_location, max_distance_km * 1000)
    ).annotate(
        distance=Distance('current_location', pickup_location)
    ).order_by('distance')[:10]  # Limit to top 10 drivers
    driver_ids = list(drivers.values_list('id', flat=True))
    cache.set(cache_key, json.dumps(driver_ids), timeout=300)  # Cache for 5 minutes

    return drivers


def geocode_address(address):
    """
    Geocode an address string to latitude and longitude using Google Geocoding API.
    Returns a dictionary with 'lat' and 'lng' or None if failed.
    """
    api_key = "AIzaSyAG3yJWxO2VrtILP7Y_6y9SAOg0Sd9bUHo"
    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'

    params = {
        'address': address,
        'key': api_key,
    }

    try:
        response = requests.get(geocode_url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return {'lat': location['lat'], 'lng': location['lng']}
        else:
            return None
    except Exception as e:
        # Log the exception
        return None

def calculate_estimated_price(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, vehicle_type):
    """
    Calculate estimated price based on distance and time using Google Distance Matrix API.
    """
    api_key = "AIzaSyAG3yJWxO2VrtILP7Y_6y9SAOg0Sd9bUHo"
    distance_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    params = {
        'origins': f"{pickup_lat},{pickup_lng}",
        'destinations': f"{dropoff_lat},{dropoff_lng}",
        'mode': 'driving',
        'departure_time': 'now',
        'traffic_model': 'best_guess',
        'key': api_key,
    }

    try:
        response = requests.get(distance_url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            element = data['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                distance_meters = element['distance']['value']
                duration_seconds = element['duration_in_traffic']['value']

                distance_km = Decimal(distance_meters) / 1000
                travel_time_min = Decimal(duration_seconds) / 60

                # Calculate price
                base_fare = vehicle_type.base_fare
                per_km = vehicle_type.per_km
                per_min = vehicle_type.per_min

                price = base_fare + (per_km * distance_km) + (per_min * travel_time_min)

                # Optionally, implement surge pricing based on demand
                surge_multiplier = get_surge_multiplier(pickup_lat, pickup_lng)
                price *= surge_multiplier

                return {
                    'estimated_price': price.quantize(Decimal('0.01')),
                    'distance_km': distance_km.quantize(Decimal('0.01')),
                    'travel_time_min': travel_time_min.quantize(Decimal('0.01')),
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        # Log the exception
        return None


def get_surge_multiplier(pickup_lat, pickup_lng):
    """
    Determine surge multiplier based on current demand vs. supply in the pickup area.
    Placeholder implementation; replace with actual logic.
    """
    # Example: Static surge multiplier
    return Decimal('1.0')