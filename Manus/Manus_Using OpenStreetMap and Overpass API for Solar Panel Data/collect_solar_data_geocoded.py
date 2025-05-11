import requests
import json
import pandas as pd
import time

def get_address_from_coords(latitude, longitude, user_agent):
    """Fetches address details from Nominatim API for given coordinates."""
    if latitude is None or longitude is None:
        return None

    api_url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}&addressdetails=1&accept-language=nl"
    headers = {"User-Agent": user_agent}
    
    try:
        # Respect Nominatim's rate limit (max 1 request per second)
        time.sleep(1.1) # Sleep for a bit more than 1 second to be safe
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("address", {})
    except requests.exceptions.Timeout:
        print(f"Timeout while fetching address for {latitude},{longitude}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching address for {latitude},{longitude}: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON for {latitude},{longitude}")
        return None

def run_collection_and_geocoding():
    overpass_url = "https://overpass-api.de/api/interpreter"
    north_holland_area_id = 47654 + 3600000000
    
    overpass_query = f"""
    [out:json][timeout:240];
    area({north_holland_area_id})->.searchArea;
    (
      way["building"]
         ["generator:source"="solar"]
         (area.searchArea);
      way["building"]
         ["roof:material"="solar_panels"]
         (area.searchArea);
      way["building"]
         ["power"="generator"]
         ["generator:source"="solar"]
         (area.searchArea);
    )->.buildings_direct_solar_tags;
    node["power"="generator"]
       ["generator:source"="solar"]
       ["location"="roof"]
       (area.searchArea)->.solar_roof_nodes;
    way[building](around.solar_roof_nodes:1)(area.searchArea)->.buildings_near_solar_nodes;
    (
      .buildings_direct_solar_tags;
      .buildings_near_solar_nodes;
    );
    out tags geom;
    """

    print("Executing Overpass query for solar buildings in North Holland...")
    print("This may take a few minutes (timeout set to 240s).")
    
    buildings_data = []
    nominatim_user_agent = "ManusAI/1.0 (Project:SolarPanelBuildingDataEnhancement; ForUser:Yes)"

    try:
        response = requests.post(overpass_url, data={"data": overpass_query}, timeout=240)
        response.raise_for_status()
        data = response.json()
        print(f"Overpass query successful. Number of elements found: {len(data.get('elements', []))}")

        elements_to_process = data.get("elements", [])
        total_elements = len(elements_to_process)
        print(f"Processing {total_elements} elements from Overpass...")

        for i, element in enumerate(elements_to_process):
            print(f"Processing element {i+1}/{total_elements} (ID: {element.get('id')})...")
            if element.get("type") == "way" and "tags" in element:
                tags = element["tags"]
                if "building" not in tags:
                    continue

                osm_id = element["id"]
                lat, lon = None, None
                geometry = element.get("geometry")
                if geometry and len(geometry) > 0:
                    first_node_geom = geometry[0]
                    lat = first_node_geom.get("lat")
                    lon = first_node_geom.get("lon")
                
                if lat is None or lon is None:
                    print(f"Warning: Could not determine coordinates for way ID {osm_id}. Skipping.")
                    continue

                street = tags.get("addr:street", "N/A")
                housenumber = tags.get("addr:housenumber", "N/A")
                postal_code = tags.get("addr:postcode", "N/A")
                city = tags.get("addr:city", "N/A")
                country = "Netherlands"
                gebruiksdoel = tags.get("building", "N/A")
                functie = tags.get("building:use", tags.get("amenity", tags.get("shop", tags.get("office", "N/A"))))

                # If address details are missing from OSM, try reverse geocoding
                if any(val == "N/A" for val in [street, housenumber, postal_code, city]):
                    print(f"  Address details incomplete for OSM ID {osm_id}. Attempting reverse geocoding...")
                    address_details = get_address_from_coords(lat, lon, nominatim_user_agent)
                    if address_details:
                        print(f"  Reverse geocoding successful for {osm_id}.")
                        street = address_details.get("road", street) # Keep OSM if Nominatim fails for this field
                        housenumber = address_details.get("house_number", housenumber)
                        postal_code = address_details.get("postcode", postal_code)
                        # Nominatim might return city, town, village, or municipality
                        city_nominatim = address_details.get("city") or address_details.get("town") or address_details.get("village") or address_details.get("municipality")
                        city = city_nominatim if city_nominatim else city
                        # Ensure country remains Netherlands if not provided by Nominatim, or if it differs
                        country_nominatim = address_details.get("country")
                        if country_nominatim and country_nominatim.lower() != "nederland":
                            print(f"  Warning: Nominatim country ({country_nominatim}) differs from expected (Netherlands) for {osm_id}")
                        else:
                            country = "Netherlands"
                    else:
                        print(f"  Reverse geocoding failed or returned no address for {osm_id}.")
                
                google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                
                buildings_data.append({
                    "Objectnummer": osm_id,
                    "Street": street,
                    "Housenumber": housenumber,
                    "Postal code": postal_code,
                    "City": city,
                    "Country": country,
                    "Gebruiksdoel": gebruiksdoel,
                    "Functie": functie,
                    "Google maps link URL": google_maps_link,
                    "Longtitude LNG": lon,
                    "Latidtude LAT": lat,
                    "OSM_Way_ID": osm_id
                })

        if not buildings_data:
            print("No building data with solar panels found or extracted.")
            headers = ["Objectnummer", "Street", "Housenumber", "Postal code", "City", "Country", 
                       "Gebruiksdoel", "Functie", "Google maps link URL", "Longtitude LNG", 
                       "Latidtude LAT", "OSM_Way_ID"]
            df = pd.DataFrame(columns=headers)
        else:
            df = pd.DataFrame(buildings_data)
        
        output_csv_path = "/home/ubuntu/north_holland_solar_buildings_geocoded.csv"
        df.to_csv(output_csv_path, index=False, encoding='utf-8')        
        if buildings_data:
            print(f"Data collection and geocoding complete. {len(df)} buildings processed.")
        else:
            print("Data collection complete. No buildings found matching criteria.")
        print(f"Results saved to: {output_csv_path}")

    except requests.exceptions.Timeout:
        print("Error: The request to Overpass API timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Error querying Overpass API: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text[:500]}")
    except json.JSONDecodeError:
        print("Error decoding JSON response from Overpass API.")
        if "response" in locals() and response is not None:
             print(f"Response status code: {response.status_code}")
             print(f"Response text (first 500 chars): {response.text[:500]}")
    except Exception as e:
        print(f"An unexpected error occurred during Overpass processing or geocoding: {e}")

if __name__ == "__main__":
    run_collection_and_geocoding()

