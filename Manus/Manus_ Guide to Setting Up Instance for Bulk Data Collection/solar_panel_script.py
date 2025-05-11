import requests
import json

# Define the Overpass API endpoint
overpass_url = "http://overpass-api.de/api/interpreter"

# Overpass QL query to find solar panels in North Holland
# (Adjust query based on specific needs and OpenStreetMap tagging conventions)
overpass_query = """
[out:json];
area(3600047654)->.searchArea;
(
  node["power"="generator"]["generator:source"="solar"](area);
  way["power"="generator"]["generator:source"="solar"](area);
  relation["power"="generator"]["generator:source"="solar"](area);
);
out body;
>;
out skel qt;
"""

# Make the Overpass API request
response = requests.post(overpass_url, data=overpass_query)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    # Process the data (e.g., print the number of solar panels found)
    print(f"Found {len(data['elements'])} solar panel related elements in North Holland.")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Further processing and analysis of the data can be added here
# For example, extracting coordinates, tags, or other relevant information
# and saving it to a CSV file or database.
