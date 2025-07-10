import requests
import pandas as pd
import math

def geocode_location(location):
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        'q': location,
        'format': 'json',
        'limit': 1
    }
    response = requests.get(url, params=params, headers={'User-Agent': 'fuel-route-api'})
    results = response.json()

    if not results:
        raise ValueError(f"Location not found: {location}")

    lat = float(results[0]['lat'])
    lon = float(results[0]['lon'])
    return [lon, lat]

def get_route_data(start, end):
    try:
        start_coords = geocode_location(start)
        end_coords = geocode_location(end)

        coords = f"{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coords}"
        osrm_params = {
            'overview': 'full',
            'geometries': 'geojson'
        }

        response = requests.get(osrm_url, params=osrm_params)
        route_data = response.json()

        if route_data.get("code") != "Ok":
            return {'error': 'Routing API failed'}

        route = route_data['routes'][0]
        distance_meters = route['distance']
        distance_miles = distance_meters / 1609.34
        geometry = route['geometry']['coordinates']

        return {
            'distance_miles': distance_miles,
            'geometry': geometry,
            'map_url': f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={start_coords[1]}%2C{start_coords[0]}%3B{end_coords[1]}%2C{end_coords[0]}"
        }
    except Exception as e:
        return {'error': str(e)}

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

def load_fuel_prices():
    df = pd.read_csv('routing/data/fuel_prices.csv')
    return df

def calculate_fuel_cost(total_distance, fuel_stops):
    mpg = 10
    gallons = total_distance / mpg
    fuel_prices = load_fuel_prices()
    avg_price = fuel_prices['price'].mean()
    return round(gallons * avg_price, 2)