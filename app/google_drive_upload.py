import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SERVICE_ACCOUNT_FILE = '../confidential/accidentframe-c9c368551f67.json'

# The folder ID of your Google Drive folder where you want to upload the images
FOLDER_ID = '1dORoEbqCijm3De0Bepq6x6jE4H0ScHP8'  # Replace with your folder ID

# Authenticate using the service account
def authenticate_google_drive():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive.file']  # This scope allows file creation and editing
    )
    return build('drive', 'v3', credentials=creds)

# Function to upload the image frame to Google Drive
def upload_frame_to_drive(image_path):
    service = authenticate_google_drive()

    # Define metadata for the file (e.g., name and folder)
    file_metadata = {
        'name': os.path.basename(image_path),  # File name
        'parents': [FOLDER_ID]  # Upload to the specified folder
    }

    # Upload the image file
    media = MediaFileUpload(image_path, mimetype='image/jpeg')  # Adjust mimetype as needed
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"File uploaded to Google Drive with ID: {file['id']}")
    return file['id']

# Function to get the file URL from the file ID
def get_file_url(file_id):
    service = authenticate_google_drive()
    
    try:
        # Retrieve the file metadata
        file = service.files().get(fileId=file_id, fields='webViewLink').execute()
        
        # The URL of the uploaded file
        file_url = file.get('webViewLink')
        print(f"File URL: {file_url}")
        return file_url
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    
def get_direct_file_url(file_id):
    # Construct the direct link URL format
    direct_url = f"https://drive.google.com/uc?id={file_id}"
    print(f"Direct File URL: {direct_url}")
    return direct_url

# Example usage: uploading an image when an accident is detected
def save_accident_frame_to_drive(frame_image_path):
    # Upload the frame and get the file ID
    file_id = upload_frame_to_drive(frame_image_path)
    
    # Get the URL for the uploaded file
    file_url = get_direct_file_url(file_id)
    
    # Return the file URL for use (e.g., for sharing with responders)
    return file_url

# Example call when an accident frame is detected
# image_path = '../static/accident_impact_frames/accident_frame1.jpg'  # Replace with your actual image path
# file_url = save_accident_frame_to_drive(image_path)

# Print the URL of the uploaded file
# if file_url:
#     print(f"Responders can view the image at: {file_url}")
