from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTextEdit, QListWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QImage, QPixmap
import sys
import cv2
import threading
import time
from datetime import datetime
from ultralytics import YOLO
import numpy as np
import os
from dotenv import load_dotenv
from optimized_hospitals import get_all_nearby_places, select_best_hospitals
from detect_accident import determine_severity
from app import accident_process

load_dotenv()
API_KEY = os.getenv("API_KEY")
lat, long = 12.969419, 80.192912
radius = 2000
place_type = "hospital"
keyword = "emergency"

def count_vehicles_inside_accident_box(vehicle_boxes, accident_box, vehicle_classes):
    if accident_box is None:
        return 0, []
    accident_x1, accident_y1, accident_x2, accident_y2 = accident_box
    involved_vehicles = set()
    for (vx1, vy1, vx2, vy2) in vehicle_boxes:
        if vx1 >= accident_x1 and vy1 >= accident_y1 and vx2 <= accident_x2 and vy2 <= accident_y2:
            involved_vehicles.update(vehicle_classes)
    return len(involved_vehicles), list(involved_vehicles)

class AccidentDetectionUI(QMainWindow):
    def __init__(self, video_source=0, conf_threshold=0.6, time_threshold=1200, show_video=True):
        super().__init__()
        self.setWindowTitle("Accident Detection System")
        self.setGeometry(100, 100, 1200, 700)
        self.video_source = video_source
        self.conf_threshold = conf_threshold
        self.time_threshold = time_threshold
        self.show_video = show_video
        
        # Main Layout
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        # Video Display (Live Accident Detection)
        self.video_label = QLabel("Live Video Feed Here")
        self.video_label.setFixedSize(640, 480)
        
        # Start and Stop Buttons
        self.start_button = QPushButton("Start Detection")
        self.stop_button = QPushButton("Stop Detection")
        
        # Search for Hospitals
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search hospitals...")
        self.search_button = QPushButton("Search")
        
        # Hospital List
        self.hospital_list = QListWidget()
        
        # Map Display (Google Maps)
        self.map_view = QWebEngineView()
        self.map_view.setFixedSize(500, 400)
        
        # Accident Details
        self.accident_details = QTextEdit()
        self.accident_details.setPlaceholderText("Accident Details (Vehicle Count, Severity, Alerts, etc.)")
        
        # Add widgets to left layout
        left_layout.addWidget(self.video_label)
        left_layout.addWidget(self.start_button)
        left_layout.addWidget(self.stop_button)
        
        # Add widgets to right layout
        right_layout.addWidget(self.search_bar)
        right_layout.addWidget(self.search_button)
        right_layout.addWidget(self.hospital_list)
        right_layout.addWidget(self.map_view)
        right_layout.addWidget(self.accident_details)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        
        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Connect buttons to functions
        self.start_button.clicked.connect(self.start_detection)
        self.stop_button.clicked.connect(self.stop_detection)
        
        # Load YOLO models
        self.vehicle_model = YOLO("../models/yolov8n.pt")  # Vehicle detection model
        self.accident_model = YOLO("../models/best.pt")    # Custom accident detection model
        
        self.running = False
    
    def start_detection(self):
        self.running = True
        threading.Thread(target=self.detect_accidents_continuously, daemon=True).start()
    
    def stop_detection(self):
        self.running = False
    
    def detect_accidents_continuously(self):
        cap = cv2.VideoCapture(self.video_source)
        last_accident_time = None
        while cap.isOpened() and self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
            current_time = time.time()
            vehicle_results = self.vehicle_model(frame)
            vehicle_boxes = []
            vehicle_info = []
            for result in vehicle_results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    vehicle_name = self.vehicle_model.names[cls]
                    vehicle_boxes.append((x1, y1, x2, y2))
                    vehicle_info.append(((x1, y1, x2, y2), vehicle_name, conf))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{vehicle_name} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            accident_results = self.accident_model(frame)
            for result in accident_results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf > self.conf_threshold:
                        accident_box = list(map(int, box.xyxy[0]))
                        cv2.rectangle(frame, (accident_box[0], accident_box[1]), (accident_box[2], accident_box[3]), (0, 0, 255), 2)
                        cv2.putText(frame, f"Accident {conf:.2f}", (accident_box[0], accident_box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        break
            
            if self.show_video:
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                qt_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_img))
            
        cap.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AccidentDetectionUI(video_source='testing.mp4')
    window.show()
    sys.exit(app.exec())
