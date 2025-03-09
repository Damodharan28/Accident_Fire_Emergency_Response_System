from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

def generate_accident_id(db):
    """Fetches and increments the accident counter to generate a unique accident ID."""
    counter_collection = db["counters"]

    # Ensure the counter exists (initialize if missing)
    if not counter_collection.find_one({"_id": "accident_id"}):
        counter_collection.insert_one({"_id": "accident_id", "seq": 125})  # Start from 125

    # Increment and fetch the updated counter value
    counter = counter_collection.find_one_and_update(
        {"_id": "accident_id"},
        {"$inc": {"seq": 1}},  # Increment counter by 1
        return_document=True
    )
    return f"Accident{counter['seq']}"

def accident_data_upload(location, acc_details, current_timestamp, responders_db):
    client = MongoClient(MONGO_URI)
    db = client["accident_db"]
    accidents_collection = db["accidents"]

    # ✅ Generate unique accident ID
    acc_id = generate_accident_id(db)

    accident_data = {
        "_id": acc_id,
        "location": location,
        "severity": acc_details[1],
        "no_of_vehicles": acc_details[0],
        "vehicles_involved": acc_details[2],
        "timestamp": current_timestamp,
        "status": "open",
        "assigned_to": None,
        "responders": responders_db
    }

    try:
        accidents_collection.insert_one(accident_data)
        print(f"✅ Accident stored successfully with ID: {acc_id}")
    except Exception as e:
        print(f"⚠️ Error storing accident: {e}")

    return acc_id

def generate_fire_id(db):
    """Fetches and increments the accident counter to generate a unique accident ID."""
    counter_collection = db["counters"]

    # Ensure the counter exists (initialize if missing)
    if not counter_collection.find_one({"_id": "fire_id"}):
        counter_collection.insert_one({"_id": "fire_id", "seq": 125})  # Start from 125

    # Increment and fetch the updated counter value
    counter = counter_collection.find_one_and_update(
        {"_id": "fire_id"},
        {"$inc": {"seq": 1}},  # Increment counter by 1
        return_document=True
    )
    return f"Fire{counter['seq']}"

def fire_data_upload(location, acc_details, current_timestamp, responders_db):
    client = MongoClient(MONGO_URI)
    db = client["accident_db"]
    accidents_collection = db["fire_accidents"]

    # ✅ Generate unique accident ID
    acc_id = generate_fire_id(db)

    accident_data = {
        "_id": acc_id,
        "location": location,
        "severity": acc_details[1],
        "no_of_vehicles": acc_details[0],
        "vehicles_involved": acc_details[2],
        "timestamp": current_timestamp,
        "status": "open",
        "assigned_to": None,
        "responders": responders_db
    }

    try:
        accidents_collection.insert_one(accident_data)
        print(f"✅ Accident stored successfully with ID: {acc_id}")
    except Exception as e:
        print(f"⚠️ Error storing accident: {e}")

    return acc_id
