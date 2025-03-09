import cv2
from ultralytics import YOLO
import os

def detect_accident(video_source=0, conf_threshold=0.6):
    """
    Detects accidents from a video or webcam using YOLOv8 for vehicle detection and best.pt for accidents.

    Args:
    video_source (str/int): Path to video file or 0 for webcam.
    conf_threshold (float): Minimum confidence score to consider an accident detection valid.

    Returns:
    first_accident_frame (numpy array): First frame where an accident is detected.
    num_vehicles (int): Number of vehicles involved.
    vehicle_types (list): Types of vehicles detected.
    """
    
    vehicle_model = YOLO("../models/yolov8n.pt")
    accident_model = YOLO("../models/accident.pt")
    fire_model = YOLO("../models/fire.pt")
    
    cap = cv2.VideoCapture(video_source)
    
    first_accident_frame = None
    num_vehicles = 0
    vehicle_types = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        vehicle_results = vehicle_model(frame)
        vehicle_classes = set()
        
        for result in vehicle_results:
            for box in result.boxes:
                cls = int(box.cls[0])
                vehicle_classes.add(vehicle_model.names[cls])
        
        accident_results = accident_model(frame)
        
        for result in accident_results:
            if any(box.conf[0] > conf_threshold for box in result.boxes):
                if first_accident_frame is None:
                    first_accident_frame = frame.copy()
                    vehicle_types = list(vehicle_classes)
                    vehicle_types.remove("airplane")
                    num_vehicles = len(vehicle_types)
                
                cap.release()
                return first_accident_frame, num_vehicles, vehicle_types
    
    cap.release()
    return None, 0, []

def determine_severity(num_vehicles, vehicle_types):
    """
    Determines the severity of an accident based on the number of vehicles and types involved.

    Args:
    num_vehicles (int): Number of vehicles involved in the accident.
    vehicle_types (list): List of vehicle types involved.

    Returns:
    str: Severity level of the accident.
    """
    severity = "Low"
    
    if num_vehicles >= 3:
        severity = "High"
    elif num_vehicles == 2:
        severity = "Moderate"
    
    if "car" in vehicle_types or "bus" in vehicle_types:
        severity = "Critical"
    
    return severity

def save_accident_frame(frame, base_folder="../static/accident_impact_frames"):
    """Saves the detected accident frame in the specified folder with an auto-incremented filename."""
    if frame is None:
        return None
    
    os.makedirs(base_folder, exist_ok=True)
    
    existing_files = [f for f in os.listdir(base_folder) if f.startswith("accident_frame_") and f.endswith(".jpg")]
    file_numbers = [int(f.split("_")[2].split(".")[0]) for f in existing_files if f.split("_")[2].split(".")[0].isdigit()]
    next_number = max(file_numbers) + 1 if file_numbers else 1
    
    filename = f"accident_frame_{next_number}.jpg"
    file_path = os.path.join(base_folder, filename)
    cv2.imwrite(file_path, frame)
    print(f"Accident frame saved at {file_path}")
    return file_path

def save_fire_accident_frame(frame, base_folder="../static/fire_impact_frames"):
    """Saves the detected accident frame in the specified folder with an auto-incremented filename."""
    if frame is None:
        return None
    
    os.makedirs(base_folder, exist_ok=True)
    
    existing_files = [f for f in os.listdir(base_folder) if f.startswith("fire_frame_") and f.endswith(".jpg")]
    file_numbers = [int(f.split("_")[2].split(".")[0]) for f in existing_files if f.split("_")[2].split(".")[0].isdigit()]
    next_number = max(file_numbers) + 1 if file_numbers else 1
    
    filename = f"fire_frame_{next_number}.jpg"
    file_path = os.path.join(base_folder, filename)
    cv2.imwrite(file_path, frame)
    print(f"Accident frame saved at {file_path}")
    return file_path
