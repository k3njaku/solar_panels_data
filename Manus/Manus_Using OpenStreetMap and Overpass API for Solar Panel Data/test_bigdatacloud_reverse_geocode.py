import requests
import json

# Sample coordinates (from previous Overpass API test - Element 1)
latitude = 52.3797364
longitude = 4.655932

print(f"Testing BigDataCloud Reverse Geocoding API for coordinates: Lat={latitude}, Lon={longitude}")

# BigDataCloud API endpoint for reverse geocoding
# Documentation: https://www.bigdatacloud.com/free-api/free-reverse-geocode-to-city-api
# The API returns locality information, we need to check if it includes street-level details.
# The API documentation states "postal code-level accuracy in the US, UK, and Australia, with partial coverage elsewhere."
# It also says "Provides both administrative and non-administrative boundary details."
# We will use the `localityLanguage=nl` for Dutch, if available, or `en`.

api_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=nl"

print(f"Requesting URL: {api_url}")

try:
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    print("\nAPI Response:")
    print(json.dumps(data, indent=2))

    # Extract relevant fields based on typical reverse geocoding responses
    # BigDataCloud's response structure needs to be inspected from the output.
    # Based on their documentation, it might be more focused on locality than specific street addresses.

    city = data.get("city") or data.get("locality")
    postcode = data.get("postcode")
    country_name = data.get("countryName")
    principal_subdivision = data.get("principalSubdivision") # e.g., state or province
    
    # Attempt to find street and housenumber if available in localityInfo or similar structures
    # This is speculative as the API is named "reverse-geocode-to-city-api"
    street = None
    housenumber = None
    
    # Example of how one might try to get more specific details if the API provides them
    # This part needs to be adjusted based on the actual API response structure
    if "localityInfo" in data and "administrative" in data["localityInfo"]:
        for admin_level in data["localityInfo"]["administrative"]:
            if admin_level.get("name") and admin_level.get("description") == "street name": # Hypothetical
                street = admin_level.get("name")
            # Similar logic for housenumber if present

    print("\nExtracted Information (if available):")
    print(f"  Latitude: {data.get('latitude')}")
    print(f"  Longitude: {data.get('longitude')}")
    print(f"  Country: {country_name}")
    print(f"  Principal Subdivision (e.g., Province): {principal_subdivision}")
    print(f"  City/Locality: {city}")
    print(f"  Postcode: {postcode}")
    print(f"  Street: {street if street else 'N/A or not provided by this API endpoint'}")
    print(f"  Housenumber: {housenumber if housenumber else 'N/A or not provided by this API endpoint'}")
    
    if not street or not postcode:
        print("\nNote: This BigDataCloud endpoint seems more focused on city/locality level. Street/housenumber might not be consistently available.")
        print("We may need to explore other APIs like Nominatim (OSM) or LocationIQ for more detailed street-level reverse geocoding.")

except requests.exceptions.Timeout:
    print("Error: The request to BigDataCloud API timed out.")
except requests.exceptions.RequestException as e:
    print(f"Error querying BigDataCloud API: {e}")
except json.JSONDecodeError:
    print("Error decoding JSON response from BigDataCloud API.")
    if 'response' in locals():
        print(f"Response status code: {response.status_code}")
        print(f"Response text (first 500 chars): {response.text[:500]}")


