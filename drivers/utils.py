import os
import requests
from dotenv import load_dotenv
from decimal import Decimal
load_dotenv()

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def get_route_data(pickup_location, dropoff_location):
    """
    Fetch route data from a mapping service (e.g., Google Maps API).
    """
    google_maps_api_key = os.getenv('MAPS_API_KEY')
    pickup_coords = f"{pickup_location.y},{pickup_location.x}"
    dropoff_coords = f"{dropoff_location.y},{dropoff_location.x}"
    
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={pickup_coords}&destination={dropoff_coords}&key={google_maps_api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        directions = response.json()
        if directions['status'] == 'OK':
            route = directions['routes'][0]['legs'][0]
            return {
                'distance': route['distance']['text'],
                'duration': route['duration']['text'],
                'steps': route['steps'],
            }
    return None