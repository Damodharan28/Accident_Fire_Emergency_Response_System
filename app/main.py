import cv2
import time
from datetime import datetime
from ultralytics import YOLO
import threading

from fire_app import fire_process
from optimized_firestations import get_all_nearby_firestations, select_best_firestations
from optimized_hospitals import get_all_nearby_places, select_best_hospitals
from detect_accident import determine_severity
from app import accident_process

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
# lat, long = get_gps_data()

lat=12.969419
long=80.192912
radius = 2000
place_type = "hospital"
keyword = "emergency"

def detect_accidents_continuously(video_source=0, conf_threshold=0.6, time_threshold=1200, show_video=True):
    """
    Continuously detects accidents in a video stream using YOLOv8.
    
    - Identifies **accidents** using `best.pt`.
    - Identifies **vehicles** using `yolov8n.pt`.
    - Counts vehicles inside the accident bounding box.
    - Differentiates multiple accidents based on a **20-minute gap**.

    Args:
        video_source (str/int): Path to video file or webcam.
        conf_threshold (float): Confidence threshold for accident detection.
        time_threshold (int): Minimum time gap (seconds) between two accidents.

    Returns:
        None (It runs indefinitely until stopped).
    """

    # Load YOLO models
    vehicle_model = YOLO("../models/yolov8n.pt")
    accident_model = YOLO("../models/accident.pt")
    fire_model = YOLO("../models/fire.pt")

    cap = cv2.VideoCapture(video_source)
    last_accident_time = None 
    last_fire_time = None
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        vehicle_results = vehicle_model(frame)
        vehicle_boxes = []
        vehicle_info = []

        for result in vehicle_results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                vehicle_name = vehicle_model.names[cls]
                vehicle_boxes.append((x1, y1, x2, y2))
                vehicle_info.append(((x1, y1, x2, y2), vehicle_name, conf))
        
       
        accident_results = accident_model(frame)
        accident_detected = False
        accident_box = None
        accident_conf = 0  # Store accident confidence separately

        for result in accident_results:
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf > conf_threshold:
                    accident_detected = True
                    accident_box = list(map(int, box.xyxy[0]))  # Get accident bounding box
                    accident_conf = conf  # Store accident confidence
                    break

        fire_results = fire_model(frame)
        fire_detected = False
        fire_box = None
        fire_conf = 0

        for result in fire_results:
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf > conf_threshold:
                    fire_detected = True
                    fire_box = list(map(int, box.xyxy[0]))  # Get fire bounding box
                    fire_conf = conf
                    break

        

        if accident_detected:
            if last_accident_time is None or (current_time - last_accident_time) > time_threshold:
                last_accident_time = current_time

                num_vehicles, involved_vehicle_types = count_vehicles_inside_accident_box(vehicle_boxes, accident_box, {v[1] for v in vehicle_info})

                nearby_places = get_all_nearby_places(lat, long, radius, place_type, API_KEY, keyword)
                severity = determine_severity(num_vehicles, involved_vehicle_types)
                if nearby_places:
                    best_hospitals = select_best_hospitals(lat, long, nearby_places, API_KEY)
                    place_ids = [hospital['place_id'] for hospital in best_hospitals]
                else:
                    place_ids = []

                accident_data = (frame, num_vehicles, severity, involved_vehicle_types, place_ids)
                accident_thread = threading.Thread(target=accident_process, args=(accident_data, lat, long, API_KEY), daemon=True)
                accident_thread.start()

        if fire_detected:
            if last_fire_time is None or (current_time - last_fire_time) > time_threshold:
                last_fire_time = current_time
                
                num_vehicles, involved_vehicle_types = count_vehicles_inside_accident_box(vehicle_boxes, fire_box, {v[1] for v in vehicle_info})
                severity = determine_severity(num_vehicles, involved_vehicle_types)
                
                fire_stations = get_all_nearby_firestations(lat, long, radius, "fire_station", API_KEY)
                if fire_stations:
                    best_fire_stations = select_best_firestations(lat, long, fire_stations, API_KEY)
                    fire_place_ids = [station['place_id'] for station in best_fire_stations]
                else:
                    fire_place_ids = []

                fire_data = (frame, num_vehicles, severity, involved_vehicle_types, fire_place_ids)
                fire_thread = threading.Thread(target=fire_process, args=(fire_data, lat, long, API_KEY), daemon=True)
                fire_thread.start()

        if show_video:
            for (x1, y1, x2, y2), vehicle_name, conf in vehicle_info:
                label = f"{vehicle_name} {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box for vehicles
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 🔥 Draw bounding box for fire with label
            if fire_box:
                cv2.rectangle(frame, (fire_box[0], fire_box[1]), (fire_box[2], fire_box[3]), (0, 165, 255), 2)  # Orange box
                cv2.putText(frame, f"🔥 Fire {fire_conf:.2f}", (fire_box[0], fire_box[1] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

            # 🚨 Draw bounding box for accident with label
            if accident_box:
                cv2.rectangle(frame, (accident_box[0], accident_box[1]), (accident_box[2], accident_box[3]), (0, 0, 255), 2)  # Red box
                cv2.putText(frame, f"🚨 Accident {accident_conf:.2f}", (accident_box[0], accident_box[1] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # ✅ Show the updated frame with fire and accident detections
            cv2.imshow("Accident and Fire Detection", frame)

            # ✅ Ensure the video keeps running
            key = cv2.waitKey(1)
            if key == ord('q'):
                break


    cap.release()
    cv2.destroyAllWindows()

    cap.release()
    cv2.destroyAllWindows()


def count_vehicles_inside_accident_box(vehicle_boxes, accident_box, vehicle_classes):
    """
    Counts how many vehicles are inside the accident bounding box.

    Args:
        vehicle_boxes (list): List of vehicle bounding boxes [(x1, y1, x2, y2)].
        accident_box (list): Accident bounding box [x1, y1, x2, y2].
        vehicle_classes (set): Detected vehicle classes.

    Returns:
        int: Number of vehicles inside accident bounding box.
        list: Types of vehicles involved.
    """
    if accident_box is None:
        return 0, []

    accident_x1, accident_y1, accident_x2, accident_y2 = accident_box
    involved_vehicles = set()

    # List of unwanted vehicle classes to ignore
    unwanted_classes = {"airplane", "train", "boat", "helicopter"}  # Add any other misdetections

    for (vx1, vy1, vx2, vy2) in vehicle_boxes:
        if is_inside(vx1, vy1, vx2, vy2, accident_x1, accident_y1, accident_x2, accident_y2):
            # Filter out unwanted vehicle classes
            filtered_classes = vehicle_classes - unwanted_classes
            involved_vehicles.update(filtered_classes)

    return len(involved_vehicles), list(involved_vehicles)


def is_inside(vx1, vy1, vx2, vy2, ax1, ay1, ax2, ay2):
    """
    Checks if a vehicle's bounding box is inside the accident bounding box.

    Args:
        vx1, vy1, vx2, vy2 (int): Vehicle bounding box coordinates.
        ax1, ay1, ax2, ay2 (int): Accident bounding box coordinates.

    Returns:
        bool: True if the vehicle is inside the accident box.
    """
    return (vx1 >= ax1 and vy1 >= ay1 and vx2 <= ax2 and vy2 <= ay2)

# Run the accident detection system
detect_accidents_continuously('fire.mp4', conf_threshold=0.6,show_video=True)
