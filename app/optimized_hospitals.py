import requests
import time
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance (Haversine) between two points on the Earth."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c  # Distance in km

def get_all_nearby_places(latitude, longitude, radius, place_type, api_key, keyword=""):
    """Fetch all nearby places (e.g., hospitals) within a radius."""
    url = "https://maps.gomaps.pro/maps/api/place/nearbysearch/json"
    params = {
        'location': f'{latitude},{longitude}',
        'radius': radius,
        'type': place_type,
        'keyword': keyword,
        'language': 'en',
        'key': api_key
    }
    
    results = []
    while True:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'results' in data:
            results.extend(data['results'])
        if 'next_page_token' in data:
            params['pagetoken'] = data['next_page_token']
            time.sleep(2)  # Short delay to handle API token refresh
        else:
            break

    return results

def get_driving_distance(origin_lat, origin_lng, destination_lat, destination_lng, api_key):
    """Get actual driving distance using the Directions API."""
    directions_url = "https://maps.gomaps.pro/maps/api/directions/json"
    directions_params = {
        'origin': f'{origin_lat},{origin_lng}',
        'destination': f'{destination_lat},{destination_lng}',
        'mode': 'driving',
        'key': api_key
    }
    response = requests.get(directions_url, params=directions_params)
    response.raise_for_status()
    data = response.json()
    
    if data['status'] == 'OK':
        return data['routes'][0]['legs'][0]['distance']['value']  # Distance in meters
    else:
        return float('inf')  # If unable to get distance, return a large number

def select_best_hospitals(latitude, longitude, places, api_key):
    """Select the best 5 hospitals based on availability and shortest distance."""
    hospitals_with_approx_distance = []

    for place in places:
        place_location = place.get('geometry', {}).get('location', {})
        if place_location:
            dest_lat = place_location.get('lat')
            dest_lng = place_location.get('lng')
            approx_distance = haversine_distance(latitude, longitude, dest_lat, dest_lng)

            # Assume higher user ratings indicate better availability
            availability = place.get('rating', 0)  # If no rating, assume 0

            hospitals_with_approx_distance.append({
                'place': place,
                'approx_distance': approx_distance,
                'availability': availability
            })

    # Sort hospitals by availability (descending) and Haversine distance (ascending)
    hospitals_with_approx_distance.sort(key=lambda x: (-x['availability'], x['approx_distance']))

    # Select the top 5 best hospitals
    top_5_hospitals = hospitals_with_approx_distance[:5]

    # Get actual driving distances for these 5 hospitals
    hospitals_with_actual_distance = []
    for item in top_5_hospitals:
        place = item['place']
        dest_lat = place['geometry']['location']['lat']
        dest_lng = place['geometry']['location']['lng']
        actual_distance = get_driving_distance(latitude, longitude, dest_lat, dest_lng, api_key)

        hospitals_with_actual_distance.append({
            'name': place['name'],
            'vicinity': place['vicinity'],
            'place_id': place['place_id'],
            'actual_distance': actual_distance
        })

    # Sort by actual driving distance
    hospitals_with_actual_distance.sort(key=lambda x: x['actual_distance'])

    return hospitals_with_actual_distance

# Example usage
API_KEY = "AlzaSyn8Qn7zw41ftsAO5Fi6DIzeo8ObRNson9C"  # Replace with your GoMapsPro API key
latitude = 12.969419  # Replace with your latitude
longitude = 80.192912  # Replace with your longitude
radius = 2000  # Search radius in meters
place_type = "hospital"  # Type of place
keyword = "emergency"  # Optional keyword

# Get nearby places (e.g., hospitals)
nearby_places = get_all_nearby_places(latitude, longitude, radius, place_type, API_KEY, keyword)

if nearby_places:
    best_hospitals = select_best_hospitals(latitude, longitude, nearby_places, API_KEY)
    place_ids = []
    print("Top 5 Best Hospitals (Sorted by Actual Distance):")
    for hospital in best_hospitals:
        print(f"{hospital['name']} - {hospital['vicinity']} - {hospital['place_id']} - Distance: {hospital['actual_distance']/1000:.2f} km")
        place_ids.append(hospital['place_id'])

    print("-----------------")
    print(place_ids)
else:
    print("No nearby emergency departments found.")
