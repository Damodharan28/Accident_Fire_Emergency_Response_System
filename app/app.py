import os
from dotenv import load_dotenv

from accident_detection import process_accident

from alert_sender import send_alerts_now

from get_place_num import get_place_details

from google_drive_upload import save_accident_frame_to_drive

from detect_accident import save_accident_frame


load_dotenv()

lat = os.getenv("LATITUDE")
long = os.getenv("LONGITUDE")
API_KEY = os.getenv("API_KEY")

lat=12.969419
long=80.192912
accident_data = process_accident(lat, long)
all_hosp_nums = []

place_ids = accident_data[-1]
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
    image_url = 'https://drive.google.com/uc?id=14o0uk4Dpw0DVgjT_tWTYjKjfRJW7aJ5z'

responders = {
    "whatsapp:+919940219151": False,
}

for num in all_hosp_nums:
    if num != None:
        if num.startswith("0"):
            num = "+91" + num[1:]
        key = f"whatsapp:{num}"
        responders[key] = False

acc_details = accident_data[1:4]
MSG = f"""🚨 *Emergency Alert* 🚨  

An accident has been detected!  

📍 *Accident Details:*  
🚗 Number of Vehicles Involved: {acc_details[0]}  
⚠️ Severity Level: {acc_details[1]}  
🚙 Vehicles Involved: {acc_details[2]}  

Your immediate response is required.  
Please acknowledge if you are available to assist.  

✅ *Reply 'YES'* to confirm your response."""


send_alerts_now(image_url, responders, MSG)








