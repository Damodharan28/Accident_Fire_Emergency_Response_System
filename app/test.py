from datetime import datetime
from mongo_db_upload import fire_data_upload

location = "12.9716, 77.5946"
acc_details = [3,"High",['car','bike']]
current_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
responders_db = [
    {"number": "whatsapp:+919876543210", "status": "pending"},
    {"number": "whatsapp:+919876543211", "status": "pending"},
    {"number": "whatsapp:+919876543212", "status": "pending"}
  ]

fire_id = fire_data_upload(location,acc_details,current_timestamp,responders_db)

print("fire :", fire_id)