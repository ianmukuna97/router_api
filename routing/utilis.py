import openrouteservice
from django.conf import settings
import pandas as pd
import math
import urllib.parse

# Read fuel prices from the CSV
def load_fuel_prices():
    df = pd.read_csv('routing/data/fuel_prices.csv')
    # CSV has 'city', 'state', and 'price' columns
    return df

# Use ORS to get route data
def get_route_data(start, end):
    try:
        client = openrouteservice.Client(key=settings.ORS_API_KEY)

        # Use geocoding to get coordinates
        start_coords = client.pelias_geocode(start)['features'][0]['geometry']['coordinates']
        end_coords = client.pelias_geocode(end)['features'][0]['geometry']['coordinates']

        coords = [start_coords, end_coords]

        route = client.directions(
            coordinates=coords,
            profile='driving-car',
            format='geojson'
        )

        distance_miles = route['features'][0]['properties']['segments'][0]['distance'] / 1609.34  # meters to miles
        geometry = route['features'][0]['geometry']['coordinates']

        map_url = f"https://maps.openrouteservice.org/directions?a={start_coords[1]},{start_coords[0]},{end_coords[1]},{end_coords[0]}"

        return {
            'distance_miles': distance_miles,
            'geometry': geometry,
            'map_url': map_url
        }
    except Exception as e:
        return {'error': str(e)}

# Fuel up every 500 miles
def find_fuel_stops(geometry, total_distance):
    max_range = 500
    stops = []
    num_stops = math.floor(total_distance / max_range)

    if num_stops == 0:
        return []

    step = len(geometry) // (num_stops + 1)
    for i in range(1, num_stops + 1):
        coord = geometry[i * step]
        lat, lon = coord[1], coord[0]
        stops.append({'lat': lat, 'lon': lon})

    return stops

# Calculate cost
def calculate_fuel_cost(total_distance, fuel_stops):
    mpg = 10
    gallons = total_distance / mpg
    fuel_prices = load_fuel_prices()

    # Assume price at each stop is closest city/state
    # For simplicity, average price
    avg_price = fuel_prices['price'].mean()

    return round(gallons * avg_price, 2)
