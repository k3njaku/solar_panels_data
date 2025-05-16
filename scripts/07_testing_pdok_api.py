import requests

# Define the WFS endpoint and parameters
wfs_url = "https://geodata.nationaalgeoregister.nl/bag/wfs"
params = {
    "service": "WFS",
    "version": "2.0.0",
    "request": "GetFeature",
    "typeNames": "bag:pand",
    "outputFormat": "application/json",
    "srsName": "EPSG:4326",
    "bbox": "4.893,52.372,4.894,52.373"  # Define a small bounding box around your point
}

response = requests.get(wfs_url, params=params)
data = response.json()

for feature in data['features']:
    properties = feature['properties']
    print(f"Building ID: {properties.get('identificatie')}")
    print(f"Usage Purpose: {properties.get('gebruiksdoel')}")
    print(f"Construction Year: {properties.get('bouwjaar')}")
    print("---")
