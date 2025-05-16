import requests
import json
import os

# Output directory
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
    print("Requesting 1,000 solar panel locations from Overpass API...")
    response = requests.post(OVERPASS_URL, data={'data': query})
    response.raise_for_status()
    data = response.json()
    print(f"Fetched {len(data['elements'])} elements.")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to: {filename}")
    return data

if __name__ == "__main__":
    fetch_solar_data()