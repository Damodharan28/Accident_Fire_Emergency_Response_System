import subprocess
import re

def get_gps_data():
    try:
        # Provide the full path to adb
        adb_path = "./platform-tools-latest-windows/platform-tools/adb.exe"  # Change this path if different
        # Run ADB command to fetch location data
        result = subprocess.run([adb_path, 'shell', 'dumpsys', 'location'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')

        # Use regex to extract latitude and longitude
        match = re.search(r'(\d+\.\d+),(-?\d+\.\d+)', output)
        if match:
            latitude, longitude = match.groups()
            return float(latitude), float(longitude)
        else:
            return None, None
    except Exception as e:
        print(f"Error fetching GPS data: {e}")
        return None, None

lat, lon = get_gps_data()
if lat and lon:
    print(f"Latitude: {lat}, Longitude: {lon}")
else:
    print("Could not fetch GPS data.")
