## Example Bulk Data Acquisition Workflow using Self-Hosted Instances

Now that you have your self-hosted Overpass API and Nominatim instances running, and your Python scripts are modified to point to them, let's outline an example workflow for bulk data acquisition. This workflow will mirror the process suggested by your scripts: collecting solar panel data using Overpass, and then enriching it with address information using Nominatim for reverse geocoding.

**Objective:** To collect data on buildings with solar panels in a specific region (e.g., North Holland), geocode them if necessary, and save the results to a CSV file.

**Workflow Steps:**

1.  **Define Your Target Region and Overpass Query:**
    *   As in your `collect_solar_data_geocoded.py` script, you have an Overpass query targeting North Holland to find buildings with solar-related tags.
    *   Ensure your self-hosted Overpass API has the data for North Holland imported and is up-to-date.

2.  **Execute the Overpass Query using Your Modified Script:**
    *   Run your modified `collect_solar_data_geocoded.py` (or a similar script derived from `collect_solar_data.py` and `solar_panel_script.py`).
    *   The script will now send the Overpass query to `http://YOUR_SERVER_IP:12345/api/interpreter`.
    *   Since it's a local instance, you can expect faster query execution and no rate limits from the API itself (though your server's capacity is the new limit).

    ```python
    # Snippet from your modified collect_solar_data_geocoded.py
    # ... (imports and setup) ...

    # Ensure this points to your local Overpass instance
    overpass_url = "http://YOUR_SERVER_IP:12345/api/interpreter" 
    # Your detailed Overpass query for North Holland solar installations
    overpass_query = f""" 
    [out:json][timeout:600]; # Increased timeout for local instance
    area({north_holland_area_id})->.searchArea;
    (
      way["building"]
         ["generator:source"="solar"]
         (area.searchArea);
      # ... (rest of your query) ...
    );
    out tags geom;
    """
    print("Executing Overpass query on self-hosted instance...")
    response = requests.post(overpass_url, data={"data": overpass_query}, timeout=600)
    data = response.json()
    elements_to_process = data.get("elements", [])
    print(f"Overpass query complete. Found {len(elements_to_process)} elements.")
    
    # ... (rest of the processing logic) ...
    ```

3.  **Process Overpass Results and Identify Geocoding Needs:**
    *   Your script iterates through the elements returned by Overpass.
    *   It extracts relevant tags (street, housenumber, city, etc.) and coordinates.
    *   If address details are incomplete from OSM tags, it flags the entry for reverse geocoding.

4.  **Perform Reverse Geocoding using Self-Hosted Nominatim:**
    *   For elements needing address enrichment, the `get_address_from_coords` function is called.
    *   This function, now modified, will send requests to your self-hosted Nominatim instance at `http://YOUR_SERVER_IP:8088/reverse`.
    *   The absence of aggressive `time.sleep()` calls means reverse geocoding for many points can proceed much faster.

    ```python
    # Snippet from your modified get_address_from_coords function
    # in collect_solar_data_geocoded.py

    # Ensure this base URL points to your local Nominatim instance
    base_nominatim_url = "http://YOUR_SERVER_IP:8088"
    api_url = f"{base_nominatim_url}/reverse?format=jsonv2&lat={latitude}&lon={longitude}&addressdetails=1&accept-language=nl"
    
    # Removed or significantly reduced time.sleep() for local instance
    response = requests.get(api_url, headers=headers, timeout=30)
    # ... (process response) ...
    ```

5.  **Collate Data and Save to CSV:**
    *   The script collects all the processed data (original OSM tags, coordinates, and reverse-geocoded address details where applicable).
    *   Finally, it saves this enriched dataset into a CSV file (e.g., `north_holland_solar_buildings_geocoded_LOCAL.csv`).

**Benefits in a Bulk Workflow:**

*   **Speed:** Both Overpass queries and Nominatim reverse geocoding requests will generally be much faster when hitting local instances, especially for large datasets, as network latency to external servers is eliminated, and you are not competing for resources.
*   **No Rate Limits:** You are not constrained by the 1 request/second limit of public Nominatim or the fair usage policies of public Overpass instances. You can process thousands or tens of thousands of geocoding requests much more rapidly. The limit becomes your server's processing capacity.
*   **Control & Reliability:** You have more control over the service availability. Public services can sometimes be down or slow.
*   **Customization:** While not covered in basic setup, advanced users can customize data imports or Overpass API configurations further if needed.

**Example Script Execution (Conceptual):**

Assuming you have a main script `run_local_solar_data_collection.py` that incorporates the modified logic from `collect_solar_data_geocoded.py`:

```bash
# Ensure your Docker containers for Overpass and Nominatim are running
docker ps

# Activate your Python environment if you use one
# source /path/to/your/venv/bin/activate

# Run your main data collection script
python3 run_local_solar_data_collection.py
```

**Expected Output during Script Execution:**

Your script's print statements will show progress:

```
Executing Overpass query on self-hosted instance...
Overpass query complete. Found XXXX elements.
Processing XXXX elements from Overpass...
Processing element 1/XXXX (ID: YYYYYYYY)...
  Address details incomplete for OSM ID YYYYYYYY. Attempting reverse geocoding on local Nominatim...
  Reverse geocoding successful for YYYYYYYY.
Processing element 2/XXXX (ID: ZZZZZZZZ)...
  Address details complete from OSM tags.
...
Data collection and geocoding complete. NNN buildings processed.
Results saved to: /home/ubuntu/north_holland_solar_buildings_geocoded_LOCAL.csv
```

**Monitoring Your Self-Hosted Services During Bulk Operations:**

When running large bulk operations, it's a good idea to monitor the resource usage on your server:

*   **CPU and Memory:** Use tools like `htop` or `docker stats` to see how much CPU and memory your Overpass and Nominatim containers are consuming.
    ```bash
    htop
    docker stats # Shows live resource usage for all running containers
    ```
*   **Disk I/O:** Tools like `iotop` can show disk read/write activity.
*   **Logs:** Keep an eye on the Docker logs for both services for any errors or warnings:
    ```bash
    docker logs -f overpass_api
    docker logs -f nominatim_service
    ```

If your server becomes overloaded, you might need to introduce small delays in your Python script between batches of requests, or consider upgrading your server hardware if you consistently hit resource limits.

This workflow, utilizing your self-hosted instances, provides a powerful and efficient way to handle the bulk data requirements of your project, directly addressing the limitations you faced with public APIs.
