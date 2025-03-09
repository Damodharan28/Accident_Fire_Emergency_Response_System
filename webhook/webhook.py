from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
import os

from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN  = os.getenv("AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

app = Flask(__name__)
client = MongoClient(MONGO_URI)
db = client["accident_db"]
accidents_collection = db["accidents"]

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    print(f"Received message from {from_number}: {incoming_msg}")

    if incoming_msg.startswith("ACK"):
        accident_id = incoming_msg.split()[-1]

        accident = accidents_collection.find_one({"_id": accident_id})
        print(accident)

        if not accident:
            response_text = "Accident ID not found."
        elif accident["status"] == "assigned":
            response_text = "This accident is already assigned."
        else:
            # Assign the responder
            print("here")
            accidents_collection.update_one(
            {"_id": accident_id},
            {"$set": {
                "status": "assigned",
                "assigned_to": from_number
            }}
            )
            accidents_collection.update_one(
            {"_id": accident_id},
            {
                "$set": {"responders.$[responder].status": "accepted"}
            },
            array_filters=[{"responder.number": from_number}]
            )

            response_text = f"You are assigned to Accident {accident_id}."
            print(response_text)
            notify_others(accident_id, from_number)

    else:
        response_text = "Invalid format. Use 'ACK AccidentID'."

    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

def notify_others(accident_id, assigned_number):
    all_responders = ["whatsapp:+919940219151"]
    from twilio.rest import Client
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    for responder in all_responders:
        if responder != assigned_number:
            client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                to=responder,
                body=f"Accident {accident_id} is already assigned."
            )

if __name__ == '__main__':
    app.run(port=5000)
