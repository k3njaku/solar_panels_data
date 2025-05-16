import json
import requests
import time
import csv

# Load your OSM data
with open('north_holland_solar_50.json', encoding='utf-8') as f:
    data = json.load(f)

results = []
for el in data['elements']:
    lat = el.get('lat')
    lon = el.get('lon')
    osm_id = el.get('id')
    if not lat or not lon:
        continue

    url = f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&addressdetails=1'
    headers = {'User-Agent': 'solar-panel-research/1.0 (your_email@example.com)'}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            print(f"Failed for {osm_id}: {resp.status_code}")
            continue
        addr = resp.json().get('address', {})
        results.append({
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
        })
        print(f"Done: {osm_id}")
    except Exception as e:
        print(f"Error for {osm_id}: {e}")
    time.sleep(1)  # Respect Nominatim usage policy!

# Write results to CSV
with open('north_holland_solar_50_filled.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print("All done! Check north_holland_solar_50_filled.csv")