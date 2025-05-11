import requests
import json

overpass_url = "https://overpass-api.de/api/interpreter"
north_holland_area_id = 47654 + 3600000000  # North Holland area ID

# Query for ways (buildings) and nodes (rooftop installations) with solar panel related tags in North Holland
overpass_query = f'''
[out:json][timeout:180];
area({north_holland_area_id})->.searchArea;
(
  // Buildings (ways) directly tagged with solar information
  way["building"]["generator:source"="solar"](area.searchArea);
  way["building"]["power"="generator"]["generator:source"="solar"](area.searchArea);
  way["building"]["roof:material"="solar_panels"](area.searchArea);

  // Nodes that are solar generators explicitly located on roofs
  node["power"="generator"]["generator:source"="solar"]["location"="roof"](area.searchArea);
);
out tags geom; // Get all tags and geometry (coordinates)
'''

print(f"Executing Overpass query for North Holland (Area ID: {north_holland_area_id}):")
print(overpass_query)

try:
    response = requests.post(overpass_url, data=overpass_query, timeout=180)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    print(f"\nNumber of elements found: {len(data.get('elements', []))}")
    print("\nSample elements (first 5, if any):")
    for i, element in enumerate(data.get('elements', [])):
        if i >= 5:
            break
        print(f"\nElement {i+1} (type: {element.get('type')}, id: {element.get('id')}):")
        if 'tags' in element:
            print("  Tags:")
            for key, value in element['tags'].items():
                print(f"    {key}: {value}")
        else:
            print("  No tags.")

        if element.get('type') == 'node':
            print(f"  Latitude: {element.get('lat')}, Longitude: {element.get('lon')}")
        elif element.get('type') == 'way':
            if 'geometry' in element and element['geometry']:
                first_node_geom = element['geometry'][0]
                print(f"  Sample geometry (first node): Lat: {first_node_geom.get('lat')}, Lon: {first_node_geom.get('lon')}")
                print(f"  Number of nodes in way geometry: {len(element['geometry'])}")
            else:
                print("  Way geometry not fully available in this sample printout (check JSON file).")
        print("-" * 20)
    
    output_file_path = "/home/ubuntu/overpass_sample_response.json"
    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nFull response saved to {output_file_path} for detailed analysis.")

except requests.exceptions.Timeout:
    print("Error: The request to Overpass API timed out after 180 seconds.")
except requests.exceptions.RequestException as e:
    print(f"Error querying Overpass API: {e}")
except json.JSONDecodeError:
    print("Error decoding JSON response from Overpass API. The response might be empty or not valid JSON.")
    if 'response' in locals():
        print(f"Response status code: {response.status_code}")
        print(f"Response text (first 500 chars): {response.text[:500]}")
    else:
        print("No response object available.")


