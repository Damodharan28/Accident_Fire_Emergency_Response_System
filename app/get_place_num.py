import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def get_place_details(place_id, api_key):
    # Base URL for the Place Details API
    url = f"https://maps.gomaps.pro/maps/api/place/details/json?place_id={place_id}&key={api_key}"

    # Parameters for the API request
    # params = {
    #     'place_id': place_id,
    #     'fields': 'name,formatted_phone_number,website,address_component',
    #     'key': api_key
    # }

    # Sending the request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Parse the JSON response
        data = response.json()
        if 'result' in data:
            return data['result']  # Return the detailed place information
        else:
            print("No details found for the given Place ID.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching details: {e}")
        return None


# API_KEY = "AlzaSyn8Qn7zw41ftsAO5Fi6DIzeo8ObRNson9C"  # Replace with your Google Maps API key
# place_id = "ChIJF6ZrhGNnUjoRHPjeO0ZF2n4"  # Replace with a Place ID from the nearby search
# place_details = get_place_details(place_id, API_KEY)

# if place_details:
#     print("Place Details:")
#     print("Name:", place_details.get("name"))
#     print("Phone:", place_details.get("formatted_phone_number"))
#     print("Website:", place_details.get("website"))
# else:
#     print("No details available.")
