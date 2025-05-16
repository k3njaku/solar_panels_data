import requests
import json

# Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Overpass QL query for solar generators in North Holland (limit 50)
query = """
[out:json][timeout:120];
area["name"="Noord-Holland"]->.searchArea;
(
  node["generator:source"="solar"](area.searchArea);
  way["generator:source"="solar"](area.searchArea);
  relation["generator:source"="solar"](area.searchArea);
);
out center 50;
"""

def fetch_solar_data():
    print("Requesting data from Overpass API...")
    response = requests.post(OVERPASS_URL, data={'data': query})
    response.raise_for_status()
    data = response.json()
    print(f"Fetched {len(data['elements'])} elements.")
    # Save to file for review (optional)
    with open('north_holland_solar_50.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

if __name__ == "__main__":
    solar_data = fetch_solar_data()
