import json
import requests
import time
import csv
import os

# Configuration
API_KEY = 'pk.ea26c8680b03eb94cb304ade3d7e494c'
INPUT_FILE = r'C:\TJ\SolarPan2\Output\north_holland_solar_1000.json'
OUTPUT_FILE = r'C:\TJ\SolarPan2\Output\north_holland_solar_1000_locationiq.csv'
MAX_RETRIES = 5
BASE_URL = 'https://eu1.locationiq.com/v1/reverse'  # Europe endpoint for faster response from NL

# Load OSM data
with open(INPUT_FILE, encoding='utf-8') as f:
    data = json.load(f)

elements = data.get('elements', [])
print(f"Total elements to process: {len(elements)}")

results = []
for idx, el in enumerate(elements, 1):
    # Extract coordinates (lat/lon for node, center for way/relation)
    lat = el.get('lat') or (el.get('center') or {}).get('lat')
    lon = el.get('lon') or (el.get('center') or {}).get('lon')
    osm_id = el.get('id')
    if not lat or not lon:
        print(f"[{idx}/{len(elements)}] Skipped: Missing coordinates (OSM id {osm_id})")
        continue

    print(f"[{idx}/{len(elements)}] Querying: {lat}, {lon} (OSM id {osm_id})")
    params = {
        'key': API_KEY,
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1
    }

    tries = 0
    while tries < MAX_RETRIES:
        try:
            resp = requests.get(BASE_URL, params=params, timeout=20)
            if resp.status_code == 200:
                addr = resp.json().get('address', {})
                row = {
                    'Objectnummer': osm_id,
                    'street': addr.get('road', ''),
                    'huisnummer': addr.get('house_number', ''),
                    'postcode': addr.get('postcode', ''),
                    'city': addr.get('city', '') or addr.get('town', '') or addr.get('village', ''),
                    'Country': addr.get('country', ''),
                    'Longitude': lon,
                    'Latitude': lat,
                    'maps_url': f"https://www.google.com/maps?q={lat},{lon}",
                    'Province': addr.get('state', ''),
                }
                print(f"[{idx}] Success: {row['city']} - {row['street']} {row['huisnummer']}")
                results.append(row)
                break
            elif resp.status_code in (403, 429):
                wait_time = 60 * (tries + 1)  # Exponential backoff: 60s, 120s, ...
                print(f"[{idx}] Blocked (HTTP {resp.status_code}). Waiting {wait_time} seconds and retrying...")
                time.sleep(wait_time)
                tries += 1
            else:
                print(f"[{idx}] Failed: HTTP {resp.status_code} for {osm_id}")
                break
        except Exception as e:
            print(f"[{idx}] Error for {osm_id}: {e}")
            break
    else:
        print(f"[{idx}] Skipped after {MAX_RETRIES} retries for {osm_id}")
    time.sleep(1)  # LocationIQ free tier: max 2 requests/second

# Save results
if results:
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"\nAll done! CSV saved to:\n{OUTPUT_FILE}")
else:
    print("No results to save.")
