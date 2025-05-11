## Modifying Existing Python Scripts to Use Self-Hosted Instances

Once your self-hosted Overpass API and Nominatim instances are up and running, the next crucial step is to modify your existing Python scripts to query these local services instead of the public ones. This will allow you to leverage the benefits of self-hosting, such as increased rate limits and faster response times for bulk data acquisition.

This section will guide you through the necessary changes in your Python scripts, using your provided files (`test_overpass.py`, `collect_solar_data.py`, `test_nominatim_reverse_geocode.py`, and `collect_solar_data_geocoded.py`) as examples.

### General Principle: Changing the API Endpoint URL

The core change in most cases involves updating the API endpoint URL in your scripts to point to your local server and the port you configured during the Docker setup.

*   **For your self-hosted Overpass API:** If you followed the Docker setup and mapped port `12345` on your host to the container's port `80`, the new endpoint will be `http://YOUR_SERVER_IP:12345/api/interpreter` or `http://localhost:12345/api/interpreter` if running on the same machine where the scripts are executed.
*   **For your self-hosted Nominatim API:** If you mapped port `8088` on your host to the container's port `8080`, the new base URL for Nominatim services (search, reverse) will be `http://YOUR_SERVER_IP:8088/` or `http://localhost:8088/`. The specific API paths (e.g., `/search`, `/reverse`) will remain the same as the public API.

Replace `YOUR_SERVER_IP` with the actual IP address of the server where you are hosting the Docker containers. If your Python scripts run on the same server as the Docker containers, you can use `localhost` or `127.0.0.1`.

### Modifying Overpass API Scripts

Let's look at how to modify scripts that use the Overpass API, such as your `test_overpass.py` and `collect_solar_data.py` (and by extension, `collect_solar_data_geocoded.py` which also uses Overpass).

**Example: `test_overpass.py` (and similar logic in `collect_solar_data.py`)**

Your original `test_overpass.py` likely has a line defining the Overpass URL:

```python
# Original line in test_overpass.py or collect_solar_data.py
overpass_url = "https://overpass-api.de/api/interpreter"
```

You need to change this to point to your local instance:

```python
# Modified line for self-hosted Overpass API
# Replace YOUR_SERVER_IP with the IP of your server, or use 'localhost' if applicable
overpass_url = "http://YOUR_SERVER_IP:12345/api/interpreter"
```

**Fuller context for `collect_solar_data.py` (or `solar_panel_script.py` as per your files):**

If your `solar_panel_script.py` (which seems to be an earlier version of `collect_solar_data.py`) looks like this:

```python
# Original solar_panel_script.py snippet
import requests

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """ # Your query here """

response = requests.post(overpass_url, data=overpass_query)
# ... rest of the script
```

The modification would be:

```python
# Modified solar_panel_script.py snippet
import requests

# Replace YOUR_SERVER_IP with the IP of your server, or use 'localhost' if applicable
overpass_url = "http://YOUR_SERVER_IP:12345/api/interpreter" 
overpass_query = """ # Your query here """

# Consider adding a timeout, especially for potentially large local queries
# You might also want to remove or adjust any aggressive rate-limiting sleeps 
# that were necessary for public APIs.
response = requests.post(overpass_url, data={"data": overpass_query}, timeout=300) # Example timeout
# ... rest of the script
```

**For `collect_solar_data_geocoded.py`:**

This script also contains an Overpass query section. The same change applies:

```python
# Original in collect_solar_data_geocoded.py
overpass_url = "https://overpass-api.de/api/interpreter"
# ...
response = requests.post(overpass_url, data={"data": overpass_query}, timeout=240)
```

Change to:

```python
# Modified in collect_solar_data_geocoded.py
# Replace YOUR_SERVER_IP with the IP of your server, or use 'localhost' if applicable
overpass_url = "http://YOUR_SERVER_IP:12345/api/interpreter"
# ...
# Adjust timeout as needed for your local instance; it can often be higher.
response = requests.post(overpass_url, data={"data": overpass_query}, timeout=600) 
```

### Modifying Nominatim API Scripts

Now let's look at scripts using Nominatim for reverse geocoding, like your `test_nominatim_reverse_geocode.py` and the geocoding part of `collect_solar_data_geocoded.py`.

**Example: `test_nominatim_reverse_geocode.py`**

Your original script might define the Nominatim URL like this:

```python
# Original line in test_nominatim_reverse_geocode.py
api_url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}"
```

Change this to use your local Nominatim instance:

```python
# Modified line for self-hosted Nominatim API
# Replace YOUR_SERVER_IP with the IP of your server, or use 'localhost' if applicable
base_nominatim_url = "http://YOUR_SERVER_IP:8088"
api_url = f"{base_nominatim_url}/reverse?format=jsonv2&lat={latitude}&lon={longitude}"
```

**For `collect_solar_data_geocoded.py` (Nominatim part):**

The `get_address_from_coords` function needs modification:

```python
# Original in get_address_from_coords function in collect_solar_data_geocoded.py
def get_address_from_coords(latitude, longitude, user_agent):
    # ...
    api_url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}&addressdetails=1&accept-language=nl"
    headers = {"User-Agent": user_agent}
    time.sleep(1.1) # Sleep for public API rate limit
    response = requests.get(api_url, headers=headers, timeout=30)
    # ...
```

Modify it as follows:

```python
# Modified get_address_from_coords function in collect_solar_data_geocoded.py
def get_address_from_coords(latitude, longitude, user_agent):
    if latitude is None or longitude is None:
        return None

    # Replace YOUR_SERVER_IP with the IP of your server, or use 'localhost' if applicable
    base_nominatim_url = "http://YOUR_SERVER_IP:8088"
    api_url = f"{base_nominatim_url}/reverse?format=jsonv2&lat={latitude}&lon={longitude}&addressdetails=1&accept-language=nl"
    
    headers = {"User-Agent": user_agent} # Still good practice to send a User-Agent
    
    # For a self-hosted instance, you can significantly reduce or remove the sleep 
    # as you control the rate limits. Monitor your server's load.
    # time.sleep(1.1) # This can likely be removed or reduced to a very small value e.g. 0.01
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30) # Adjust timeout if needed
        response.raise_for_status()
        data = response.json()
        return data.get("address", {})
    # ... (rest of the error handling)
```

**Important Considerations When Modifying Scripts:**

1.  **User-Agent:** It's still good practice to send a descriptive `User-Agent` header, even to your own services. This helps in logging and debugging if you have multiple scripts or services accessing your APIs.
2.  **Rate Limiting (`time.sleep`):** One of the main reasons for self-hosting is to overcome strict public API rate limits. You can significantly reduce or remove `time.sleep()` calls that were added to respect public server policies. However, monitor your self-hosted server's performance. If you send too many requests too quickly, you might still overload your own server, especially if it's not very powerful.
3.  **Timeouts:** For local instances, network latency is usually much lower. However, complex queries or a heavily loaded server might still take time. Adjust request timeouts (`timeout` parameter in `requests.get` or `requests.post`) appropriately. You might be able to use longer timeouts for complex Overpass queries if your server can handle them.
4.  **Error Handling:** Keep robust error handling in your scripts. Even local services can sometimes fail or return unexpected responses (e.g., during startup, if the database is being updated, or if a query is malformed).
5.  **Configuration:** Instead of hardcoding `YOUR_SERVER_IP` and ports directly in multiple scripts, consider using a configuration file (e.g., `config.ini`, `config.json`, or environment variables) to store these details. This makes it easier to manage and change if your server IP or port mappings change in the future.

    Example using a simple config dictionary (for illustration):

    ```python
    # config.py
    CONFIG = {
        "OVERPASS_API_URL": "http://localhost:12345/api/interpreter",
        "NOMINATIM_API_URL": "http://localhost:8088"
    }
    ```

    Then in your scripts:

    ```python
    # In your main script
    from config import CONFIG

    overpass_url = CONFIG["OVERPASS_API_URL"]
    base_nominatim_url = CONFIG["NOMINATIM_API_URL"]
    # ... then use these variables
    ```

By making these changes, your Python scripts will now communicate with your self-hosted Overpass API and Nominatim services, enabling you to perform bulk data acquisition and geocoding tailored to your project's needs.
