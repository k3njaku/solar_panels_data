## Integrating Self-Hosted Services into Your Existing Workflow

This section provides practical steps on how to integrate the self-hosted Overpass API and Nominatim services, along with the modified Python scripts, into your existing project structure for bulk data acquisition.

### 1. Project Directory Structure (Suggestion)

To keep things organized, consider a project structure like this:

```
your_project_directory/
├── original_scripts/                  # Your original Python scripts (as a backup or reference)
│   ├── collect_solar_data.py
│   └── collect_solar_data_geocoded.py
│   └── ... (other original files)
├── self_hosted_scripts/               # Modified Python scripts for self-hosted services
│   ├── config.py                        # NEW: For API endpoints and settings
│   └── run_solar_data_collection_local.py # NEW: Your main script, adapted for local APIs
├── docker_setup/
│   ├── overpass_api/
│   │   ├── docker-compose.yml           # Example Overpass docker-compose file
│   │   └── osm_data/                    # Place your netherlands-latest.osm.pbf here
│   └── nominatim_api/
│       ├── docker-compose.yml           # Example Nominatim docker-compose file
│       └── osm_data/                    # Can share the same PBF or have its own copy
├── output_data/
│   └── north_holland_solar_buildings_geocoded_LOCAL.csv # Output from your script
└── README.md                          # Project overview and instructions
```

*   **`original_scripts/`**: Keep your original scripts untouched for reference.
*   **`self_hosted_scripts/`**: This is where you'll place the Python scripts modified to use your local Overpass and Nominatim instances. We'll create a `config.py` for managing API URLs and a main script like `run_solar_data_collection_local.py`.
*   **`docker_setup/`**: Contains the `docker-compose.yml` files for Overpass and Nominatim, and the `osm_data` subdirectories where you will place the downloaded OpenStreetMap PBF file (e.g., `netherlands-latest.osm.pbf`).
*   **`output_data/`**: Where your processed CSV files will be saved.

### 2. Setting Up and Running Docker Services

1.  **Prepare Docker Compose Files:**
    *   Copy the `example_overpass_docker-compose.yml` provided in this guide to `your_project_directory/docker_setup/overpass_api/docker-compose.yml`.
    *   Copy the `example_nominatim_docker-compose.yml` to `your_project_directory/docker_setup/nominatim_api/docker-compose.yml`.
    *   **Important:** Review each `docker-compose.yml` file. Ensure the paths to your OSM PBF file (e.g., `/osm_data/netherlands-latest.osm.pbf` inside the container) and the host volume mounts for data persistence (e.g., `/srv/overpass_db_example`, `/srv/nominatim_data_example`) are correct for your system. Adjust memory/CPU limits if needed.

2.  **Download OSM Data:**
    *   Download `netherlands-latest.osm.pbf` (or your desired region) from Geofabrik.
    *   Place it into `your_project_directory/docker_setup/overpass_api/osm_data/`.
    *   Place it (or a copy) into `your_project_directory/docker_setup/nominatim_api/osm_data/`.

3.  **Create Host Directories for Data Persistence:**
    *   As specified in the comments of the example `docker-compose.yml` files, create the directories on your host machine that will store the database data. For example:
        ```bash
        sudo mkdir -p /srv/overpass_db_example && sudo chown $(whoami):$(whoami) /srv/overpass_db_example
        sudo mkdir -p /srv/nominatim_data_example && sudo chown -R 999:999 /srv/nominatim_data_example
        ```
        (Adjust paths and ownership as per your `docker-compose.yml` and the user IDs within the containers if they differ).

4.  **Start the Services:**
    *   Navigate to the Overpass directory and start it:
        ```bash
        cd your_project_directory/docker_setup/overpass_api/
        docker-compose up -d
        ```
    *   Navigate to the Nominatim directory and start it:
        ```bash
        cd your_project_directory/docker_setup/nominatim_api/
        docker-compose up -d 
        ```
    *   **Monitor Initial Import:** Remember that the initial data import for both services (especially Nominatim) will take a significant amount of time. Monitor the logs as described in the setup sections:
        ```bash
        docker logs -f overpass_api_example
        docker logs -f nominatim_service_example 
        ```
        Wait for the imports to complete before running your data collection scripts.

### 3. Adapting Your Python Scripts

1.  **Create `config.py`:**
    Inside `your_project_directory/self_hosted_scripts/`, create a file named `config.py`:

    ```python
    # self_hosted_scripts/config.py

    # Replace 'YOUR_SERVER_IP' with the actual IP address of your server where Docker is running.
    # If your Python script runs on the SAME machine as the Docker containers, you can use 'localhost'.
    SERVER_IP = 'localhost' # Or 'YOUR_SERVER_IP'

    OVERPASS_API_CONFIG = {
        "url": f"http://{SERVER_IP}:12345/api/interpreter",
        "timeout": 600  # Default timeout for Overpass queries in seconds
    }

    NOMINATIM_API_CONFIG = {
        "base_url": f"http://{SERVER_IP}:8088", # Base URL for Nominatim (search, reverse)
        "user_agent": "YourProject/1.0 (ManusAI; YourContactInfo)",
        "timeout": 30,   # Default timeout for Nominatim requests in seconds
        "sleep_interval": 0.01 # Minimal sleep between requests to local Nominatim (adjust as needed)
    }

    # Define your North Holland Area ID (or other relevant constants)
    NORTH_HOLLAND_AREA_ID = 47654 + 3600000000

    # Output file path
    OUTPUT_CSV_PATH = "../output_data/north_holland_solar_buildings_geocoded_LOCAL.csv"
    ```

2.  **Create/Adapt `run_solar_data_collection_local.py`:**
    This will be your main script, based on your `collect_solar_data_geocoded.py`. Place it in `your_project_directory/self_hosted_scripts/`.

    ```python
    # self_hosted_scripts/run_solar_data_collection_local.py
    import requests
    import json
    import pandas as pd
    import time
    from config import OVERPASS_API_CONFIG, NOMINATIM_API_CONFIG, NORTH_HOLLAND_AREA_ID, OUTPUT_CSV_PATH

    def get_address_from_coords_local(latitude, longitude):
        """Fetches address details from self-hosted Nominatim API."""
        if latitude is None or longitude is None:
            return None

        api_url = f"{NOMINATIM_API_CONFIG['base_url']}/reverse?format=jsonv2&lat={latitude}&lon={longitude}&addressdetails=1&accept-language=nl"
        headers = {"User-Agent": NOMINATIM_API_CONFIG['user_agent']}
        
        try:
            # Reduced sleep for local instance
            time.sleep(NOMINATIM_API_CONFIG['sleep_interval'])
            response = requests.get(api_url, headers=headers, timeout=NOMINATIM_API_CONFIG['timeout'])
            response.raise_for_status()
            data = response.json()
            return data.get("address", {})
        except requests.exceptions.Timeout:
            print(f"Timeout while fetching address for {latitude},{longitude} from local Nominatim")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching address for {latitude},{longitude} from local Nominatim: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON for {latitude},{longitude} from local Nominatim")
            return None

    def run_collection_and_geocoding_local():
        overpass_url = OVERPASS_API_CONFIG['url']
        overpass_timeout = OVERPASS_API_CONFIG['timeout']
        
        # Your Overpass query (can be loaded from a file or defined here)
        overpass_query = f"""
        [out:json][timeout:{overpass_timeout}];
        area({NORTH_HOLLAND_AREA_ID})->.searchArea;
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

        print(f"Executing Overpass query on self-hosted instance: {overpass_url}")
        print(f"Timeout set to {overpass_timeout}s.")
        
        buildings_data = []

        try:
            response = requests.post(overpass_url, data={"data": overpass_query}, timeout=overpass_timeout)
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
                        # For simplicity, take the first node of the way as its representative point
                        # More sophisticated methods (centroid) could be used if needed
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
                    country = "Netherlands" # Assuming Netherlands for this project
                    gebruiksdoel = tags.get("building", "N/A")
                    functie = tags.get("building:use", tags.get("amenity", tags.get("shop", tags.get("office", "N/A"))))

                    if any(val == "N/A" for val in [street, housenumber, postal_code, city]):
                        print(f"  Address details incomplete for OSM ID {osm_id}. Attempting reverse geocoding with local Nominatim...")
                        address_details = get_address_from_coords_local(lat, lon)
                        if address_details:
                            print(f"  Reverse geocoding successful for {osm_id}.")
                            street = address_details.get("road", street)
                            housenumber = address_details.get("house_number", housenumber)
                            postal_code = address_details.get("postcode", postal_code)
                            city_nominatim = address_details.get("city") or address_details.get("town") or address_details.get("village") or address_details.get("municipality")
                            city = city_nominatim if city_nominatim else city
                            country_nominatim = address_details.get("country")
                            if country_nominatim and country_nominatim.lower() != "nederland":
                                print(f"  Warning: Nominatim country ({country_nominatim}) differs from expected (Netherlands) for {osm_id}")
                            country = "Netherlands" # Re-assert
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
                # Define headers even if no data, for an empty CSV with correct columns
                headers = ["Objectnummer", "Street", "Housenumber", "Postal code", "City", "Country", 
                           "Gebruiksdoel", "Functie", "Google maps link URL", "Longtitude LNG", 
                           "Latidtude LAT", "OSM_Way_ID"]
                df = pd.DataFrame(columns=headers)
            else:
                df = pd.DataFrame(buildings_data)
            
            df.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8')
            if buildings_data:
                print(f"Data collection and geocoding complete. {len(df)} buildings processed.")
            else:
                print("Data collection complete. No buildings found matching criteria.")
            print(f"Results saved to: {OUTPUT_CSV_PATH}")

        except requests.exceptions.Timeout as e:
            print(f"Error: The request to Overpass API timed out: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error querying Overpass API: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text[:500]}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response from Overpass API: {e}")
            if 'response' in locals() and response is not None:
                 print(f"Response status code: {response.status_code}")
                 print(f"Response text (first 500 chars): {response.text[:500]}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        run_collection_and_geocoding_local()
    ```
    **Key changes in this adapted script:**
    *   Imports configuration from `config.py`.
    *   Uses API URLs and settings from the config.
    *   The `get_address_from_coords_local` function is adapted for the local Nominatim instance (URL, reduced sleep).
    *   The main Overpass query uses the configured timeout.
    *   Output path is taken from `config.py`.

### 4. Running Your Integrated Workflow

1.  **Ensure Services are Ready:** Confirm your Overpass API and Nominatim Docker containers are running and have completed their initial data imports.
2.  **Navigate to Scripts Directory:**
    ```bash
    cd your_project_directory/self_hosted_scripts/
    ```
3.  **Activate Python Environment (if you use one):**
    ```bash
    # e.g., source ../my_env/bin/activate
    ```
4.  **Run the Script:**
    ```bash
    python3 run_solar_data_collection_local.py
    ```
5.  **Check Outp
(Content truncated due to size limit. Use line ranges to read in chunks)