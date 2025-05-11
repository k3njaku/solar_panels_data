import requests
import json
import pandas as pd

def run_collection():
    overpass_url = "https://overpass-api.de/api/interpreter"
    # Relation ID for North Holland is 47654. For Overpass area ID, add 3600000000.
    north_holland_area_id = 47654 + 3600000000
    
    # Refined Overpass query to get building ways with solar panels
    # Timeout is set to 240 seconds for potentially long query
    overpass_query = f"""
    [out:json][timeout:240];
    area({north_holland_area_id})->.searchArea;

    // Set 1: Buildings (ways) directly tagged with solar information
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

    // Set 2: Find solar generator nodes on roofs
    node["power"="generator"]
       ["generator:source"="solar"]
       ["location"="roof"]
       (area.searchArea)->.solar_roof_nodes;

    // Find buildings (ways) that are very close to these solar roof nodes
    // (around:1) means within 1 meter of the node's center.
    way[building](around.solar_roof_nodes:1)(area.searchArea)->.buildings_near_solar_nodes;

    // Combine all found building ways
    (
      .buildings_direct_solar_tags;
      .buildings_near_solar_nodes;
    );

    // Output the combined set of buildings with their tags and geometry
    out tags geom;
    """

    print("Executing Overpass query for solar buildings in North Holland...")
    print("This may take a few minutes (timeout set to 240s).")
    
    buildings_data = []
    
    try:
        response = requests.post(overpass_url, data={'data': overpass_query}, timeout=240)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        print(f"Query successful. Number of elements found: {len(data.get('elements', []))}")

        for element in data.get('elements', []):
            if element.get('type') == 'way' and 'tags' in element: # Ensure it's a way and has tags
                tags = element['tags']
                
                # Only process if it's explicitly a building
                if 'building' not in tags:
                    continue

                osm_id = element['id']
                
                lat, lon = None, None
                geometry = element.get('geometry')
                if geometry and len(geometry) > 0:
                    # Use coordinates of the first node in the way's geometry as representative
                    first_node_geom = geometry[0]
                    lat = first_node_geom.get('lat')
                    lon = first_node_geom.get('lon')
                
                if lat is None or lon is None:
                    print(f"Warning: Could not determine coordinates for way ID {osm_id}. Skipping.")
                    continue

                # Extract required fields
                objectnummer = osm_id
                street = tags.get('addr:street', 'N/A')
                housenumber = tags.get('addr:housenumber', 'N/A')
                postal_code = tags.get('addr:postcode', 'N/A')
                city = tags.get('addr:city', 'N/A')
                country = "Netherlands" # Fixed for North Holland
                
                gebruiksdoel = tags.get('building', 'N/A')
                
                functie = tags.get('building:use', 
                                   tags.get('amenity', 
                                            tags.get('shop', 
                                                     tags.get('office', 'N/A'))))
                
                google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                
                buildings_data.append({
                    "Objectnummer": objectnummer,
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
                    "OSM_Way_ID": osm_id # Add for reference
                })

        if not buildings_data:
            print("No building data with solar panels found or extracted.")
            # Create an empty CSV with headers if no data
            headers = ["Objectnummer", "Street", "Housenumber", "Postal code", "City", "Country", 
                       "Gebruiksdoel", "Functie", "Google maps link URL", "Longtitude LNG", 
                       "Latidtude LAT", "OSM_Way_ID"]
            df = pd.DataFrame(columns=headers)
        else:
            df = pd.DataFrame(buildings_data)
        
        output_csv_path = "/home/ubuntu/north_holland_solar_buildings.csv"
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        
        if buildings_data:
            print(f"Data collection complete. {len(df)} buildings processed.")
        else:
            print("Data collection complete. No buildings found matching criteria.")
        print(f"Results saved to: {output_csv_path}")

    except requests.exceptions.Timeout:
        print("Error: The request to Overpass API timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Error querying Overpass API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text[:500]}")
    except json.JSONDecodeError:
        print("Error decoding JSON response from Overpass API.")
        if 'response' in locals() and response is not None:
             print(f"Response status code: {response.status_code}")
             print(f"Response text (first 500 chars): {response.text[:500]}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Call the main function when the script is executed
run_collection()

