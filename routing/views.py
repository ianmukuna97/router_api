from django.http import JsonResponse
from .utilis import get_route_data, find_fuel_stops, calculate_fuel_cost

def route_api(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    if not start or not end:
        return JsonResponse({'error': 'start and end parameters are required'}, status=400)

    route_data = get_route_data(start, end)
    if 'error' in route_data:
        return JsonResponse(route_data, status=500)

    fuel_stops = find_fuel_stops(route_data['geometry'], route_data['distance_miles'])
    total_cost = calculate_fuel_cost(route_data['distance_miles'], fuel_stops)

    return JsonResponse({
        'route_map_url': route_data['map_url'],
        'fuel_stops': fuel_stops,
        'total_fuel_cost_usd': total_cost
    })
