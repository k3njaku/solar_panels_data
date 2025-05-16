import json
import requests
import time
import csv
import os

output_dir = r'C:\TJ\SolarPan2\Output'
input_file = os.path.join(output_dir, 'north_holland_solar_1000.json')
output_file = os.path.join(output_dir, 'north_holland_solar_1000_filled.csv')

headers = {'User-Agent': 'solar-panel-research/1.0 (your_email@example.com)'}

max_retries = 5

with open(input_file, encoding='utf-8') as f:
    data = json.load(f)

elements = data.get('elements', [])
print(f"Total elements to process: {len(elements)}")

results = []
for idx, el in enumerate(elements, 1):
    # Use lat/lon if present, otherwise try center
    lat = el.get('lat') or (el.get('center') or {}).get('lat')
    lon = el.get('lon') or (el.get('center') or {}).get('lon')
    osm_id = el.get('id')
    if not lat or not lon:
        print(f"[{idx}/{len(elements)}] Skipped: Missing coordinates (OSM id {osm_id})")
        continue

    print(f"[{idx}/{len(elements)}] Querying: {lat}, {lon} (OSM id {osm_id})")
    url = f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&addressdetails=1'
    tries = 0
    while tries < max_retries:
        try:
            resp = requests.get(url, headers=headers, timeout=20)
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
                wait_time = 60 * (tries + 1)  # Exponential backoff
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
        print(f"[{idx}] Skipped after {max_retries} retries for {osm_id}")
    time.sleep(1)  # Respect Nominatim usage policy

# Save results
if results:
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"\nAll done! CSV saved to:\n{output_file}")
else:
    print("No results to save.")
