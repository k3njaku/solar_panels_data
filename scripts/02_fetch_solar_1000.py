import requests
import json
import os
import datetime

# Output directory and filename
output_dir = r'C:\TJ\SolarPan2\Output'
os.makedirs(output_dir, exist_ok=True)
filename = os.path.join(output_dir, 'north_holland_solar_1000.json')

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

query = """
[out:json][timeout:300];
area["name"="Noord-Holland"]->.searchArea;
(
  node["generator:source"="solar"](area.searchArea);
  way["generator:source"="solar"](area.searchArea);
  relation["generator:source"="solar"](area.searchArea);
);
out center 1000;
"""

def fetch_solar_data():
    print(f"\n[{datetime.datetime.now()}] Starting Overpass API request for 1,000 solar panel locations...")
    try:
        response = requests.post(OVERPASS_URL, data={'data': query}, timeout=300)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.datetime.now()}] ERROR: Failed to contact Overpass API: {e}")
        return

    print(f"[{datetime.datetime.now()}] Data received, parsing JSON...")
    data = response.json()
    element_count = len(data.get('elements', []))
    print(f"[{datetime.datetime.now()}] Total solar panel objects fetched: {element_count}")

    # Log coordinate types
    direct_coords = 0
    center_coords = 0
    missing_coords = 0
    for el in data.get('elements', []):
        if 'lat' in el and 'lon' in el:
            direct_coords += 1
        elif 'center' in el and 'lat' in el['center'] and 'lon' in el['center']:
            center_coords += 1
        else:
            missing_coords += 1

    print(f"Entries with direct lat/lon: {direct_coords}")
    print(f"Entries with center lat/lon: {center_coords}")
    print(f"Entries missing coordinates: {missing_coords}")

    if element_count < 1000:
        print(f"[{datetime.datetime.now()}] WARNING: Only {element_count} elements found (less than 1,000). This may be all available data.")

    # Save file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[{datetime.datetime.now()}] Data saved to: {filename}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ERROR: Could not save file: {e}")

    print(f"[{datetime.datetime.now()}] Process completed.\n")

if __name__ == "__main__":
    fetch_solar_data()
