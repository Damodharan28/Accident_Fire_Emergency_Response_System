import cv2
import random
from optimized_hospitals import get_all_nearby_places, select_best_hospitals
from detect_accident import detect_accident, determine_severity
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def process_accident(latitude, longitude):
    """Detects an accident and fetches the nearest hospitals."""
    print("Accident detected!")
    
    frame, num_vehicles, vehicle_types = detect_accident("testing.mp4", conf_threshold=0.6)
    severity = determine_severity(num_vehicles, vehicle_types)
    
    print(f"Vehicles involved: {num_vehicles}, Severity: {severity}, Types: {vehicle_types}")
    
    radius = 2000
    place_type = "hospital"
    keyword = "emergency"
    
    nearby_places = get_all_nearby_places(latitude, longitude, radius, place_type, API_KEY, keyword)
    
    if nearby_places:
        best_hospitals = select_best_hospitals(latitude, longitude, nearby_places, API_KEY)
        place_ids = [hospital['place_id'] for hospital in best_hospitals]
        return frame,num_vehicles, severity, vehicle_types, place_ids
    else:
        print("No nearby emergency hospitals found.")
        return frame, num_vehicles, severity, vehicle_types, []
    
    # return None, None, None, None, []  # No accident detected

