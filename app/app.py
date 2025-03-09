import os
from dotenv import load_dotenv
from accident_detection import process_accident
from alert_sender import send_alerts_now
from get_place_num import get_place_details
from google_drive_upload import save_accident_frame_to_drive
from detect_accident import save_accident_frame
from mongo_db_upload import accident_data_upload
# from get_lat_long import get_gps_data
from optimized_hospitals import get_all_nearby_places,select_best_hospitals


def accident_process(accident_data, lat, long, API_KEY):
    place_ids = accident_data[-1]
    all_hosp_nums = []
    print("place_ids" , place_ids)
    for place_id in place_ids:
        place_details = get_place_details(place_id, API_KEY)
        all_hosp_nums.append(place_details.get("formatted_phone_number"))

    print("numbers" , all_hosp_nums)


    # image_url = 'https://drive.google.com/uc?id=14o0uk4Dpw0DVgjT_tWTYjKjfRJW7aJ5z'
    frame = accident_data[0]
    if frame is not None:
        file_path = save_accident_frame(frame)
        image_url = save_accident_frame_to_drive(file_path)
    else:
        # image_url = 'https://drive.google.com/uc?id=14o0uk4Dpw0DVgjT_tWTYjKjfRJW7aJ5z'
        image_url = None

    responders = {
        "whatsapp:+919940219151": False,
    }

    

    for num in all_hosp_nums:
        if num != None:
            if num.startswith("0"):
                num = "+91" + num[1:]
            key = f"whatsapp:{num}"
            responders[key] = False

    responders_db = []

    for key,val in responders.items():
        responders_db.append({"number":key,"status":"pending"})

    location = f"{lat}, {long}"
    from datetime import datetime
    current_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    acc_details = accident_data[1:4]

    accident_id = accident_data_upload(location=location,acc_details=acc_details,current_timestamp=current_timestamp,responders_db=responders_db)

    MSG = f"""🚨 *Emergency Alert* 🚨  

    An accident has been detected! 
    *Accident ID :* {accident_id} 

    📍 *Accident Details:*  
    🚗 Number of Vehicles Involved: {acc_details[0]}  
    ⚠️ Severity Level: {acc_details[1]}  
    🚙 Vehicles Involved: {acc_details[2]}  

    Your immediate response is required.  
    Please acknowledge if you are available to assist.  

    ✅ *Reply "ACK 'accident_id'" to confirm your response."""


    send_alerts_now(image_url, responders, MSG)








