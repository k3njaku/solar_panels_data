# self_hosted_scripts/config.py

# Replace 'YOUR_SERVER_IP' with the actual IP address of your server where Docker is running.
# If your Python script runs on the SAME machine as the Docker containers, you can use 'localhost'.
SERVER_IP = 'localhost' # Or 'YOUR_SERVER_IP'

OVERPASS_API_CONFIG = {
    "url": f"http://{SERVER_IP}:12345/api/interpreter",
    "timeout": 600  # Default timeout for Overpass queries in seconds
}

NOMINATIM_API_CONFIG = {
    "base_url": f"http://{SERVER_IP}:8088", # Base URL for Nominatim (search, reverse)
    "user_agent": "YourProject/1.0 (ManusAI; YourContactInfo)",
    "timeout": 30,   # Default timeout for Nominatim requests in seconds
    "sleep_interval": 0.01 # Minimal sleep between requests to local Nominatim (adjust as needed)
}

# Define your North Holland Area ID (or other relevant constants)
NORTH_HOLLAND_AREA_ID = 47654 + 3600000000

# Output file path, assuming this script is in 'self_hosted_scripts' and output is in 'output_data'
OUTPUT_CSV_PATH = "../output_data/north_holland_solar_buildings_geocoded_LOCAL.csv"

