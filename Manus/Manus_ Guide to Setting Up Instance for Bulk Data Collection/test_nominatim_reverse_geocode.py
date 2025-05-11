import requests
import json
import time

# Sample coordinates (from previous Overpass API test - Element 1)
latitude = 52.3797364
longitude = 4.655932

print(f"Testing Nominatim (OpenStreetMap) Reverse Geocoding API for coordinates: Lat={latitude}, Lon={longitude}")

# Nominatim API endpoint for reverse geocoding
# Documentation: https://nominatim.org/release-docs/latest/api/Reverse/
# Usage Policy: https://operations.osmfoundation.org/policies/nominatim/ (Max 1 req/sec, provide User-Agent)

api_url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}&addressdetails=1&accept-language=nl"

# It is crucial to set a User-Agent as per Nominatim's usage policy
headers = {
    "User-Agent": "ManusAI/1.0 (Project: SolarPanelBuildingData; Contact: user_project_contact_info_not_available)"
}

print(f"Requesting URL: {api_url}")

try:
    # Respect rate limit (1 request per second)
    # time.sleep(1) # Add delay if making multiple requests in a loop, not strictly needed for a single test.
    
    response = requests.get(api_url, headers=headers, timeout=30)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    print("\nAPI Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Extract relevant fields from the 'address' object in the response
    address_details = data.get("address", {})
    
    street = address_details.get("road")
    housenumber = address_details.get("house_number")
    postcode = address_details.get("postcode")
    # City can be in 'city', 'town', or 'village' depending on the location type
    city = address_details.get("city") or address_details.get("town") or address_details.get("village") or address_details.get("municipality")
    country_name = address_details.get("country")
    country_code = address_details.get("country_code")
    state = address_details.get("state") # Province in NL context

    print("\nExtracted Address Information:")
    print(f"  Street: {street if street else 'N/A'}")
    print(f"  House Number: {housenumber if housenumber else 'N/A'}")
    print(f"  Postcode: {postcode if postcode else 'N/A'}")
    print(f"  City/Town/Village: {city if city else 'N/A'}")
    print(f"  Province/State: {state if state else 'N/A'}")
    print(f"  Country: {country_name if country_name else 'N/A'} ({country_code.upper() if country_code else 'N/A'})")

    if street and postcode and city:
        print("\nNote: Nominatim appears to provide detailed street-level information.")
    else:
        print("\nNote: Some address details might be missing. Check the full API response.")
        if not street:
            print("  - Street name (road) not found.")
        if not housenumber:
            print("  - House number not found.")
        if not postcode:
            print("  - Postcode not found.")
        if not city:
            print("  - City/Town/Village not found.")

except requests.exceptions.Timeout:
    print("Error: The request to Nominatim API timed out.")
except requests.exceptions.RequestException as e:
    print(f"Error querying Nominatim API: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text[:500]}")
except json.JSONDecodeError:
    print("Error decoding JSON response from Nominatim API.")
    if 'response' in locals() and response is not None:
         print(f"Response status code: {response.status_code}")
         print(f"Response text (first 500 chars): {response.text[:500]}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


