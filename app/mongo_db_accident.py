
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://accidentdetectioncse2024:I7A5XWFml8VFAfFQ@clusteraccident.mvst9.mongodb.net/?retryWrites=true&w=majority&appName=ClusterAccident"

accident_data = {
  "_id": "Fire125",
  "location": "12.9716, 77.5946",
  "severity": "High",
  "vehicles_involved": 3,
  "timestamp": "2025-02-21T10:30:00Z",
  "status": "open",
  "assigned_to": None,  
  "responders": [
    {"number": "whatsapp:+919876543210", "status": "pending"},
    {"number": "whatsapp:+919876543211", "status": "pending"},
    {"number": "whatsapp:+919876543212", "status": "pending"}
  ]
}

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["accident_db"]

accidents_collection = db["fire_accidents"]

try:
    accidents_collection.insert_one(accident_data)
    print(f"✅ Accident stored successfully.")
except Exception as e:
    print(f"⚠️ Error storing accident: {e}")