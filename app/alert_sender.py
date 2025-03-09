from twilio.rest import Client
import time

import os
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp_alert(to_number, message, media_url):
    try:
        whatsapp_message = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number,
            media_url=[media_url]
        )
        print(f"WhatsApp message sent to {to_number}: SID {whatsapp_message.sid}")
    except Exception as e:
        print(f"Error sending WhatsApp message to {to_number}: {e}")

# Function to send WhatsApp alerts to all responders immediately
def send_alerts_now(img_url, responders, MSG):
    print(f"Sending emergency WhatsApp alerts at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    for responder in responders:
        send_whatsapp_alert(
            to_number=responder,
            message=MSG,
            media_url=img_url
        )
    print("All alerts sent.")

# Function to alert responders based on accident detection
def alert_responder(accident_status, img_url):
    """
    Sends an alert to the responder if an accident is detected.
    """
    if accident_status:
        print("Accident detected! Sending alert to responders...")
        send_alerts_now(img_url)  # Trigger the WhatsApp alerts
    else:
        print("No accident detected. No alert sent.")
