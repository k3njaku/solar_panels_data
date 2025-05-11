## Troubleshooting Common Issues

Setting up and running self-hosted Overpass API and Nominatim instances can sometimes present challenges. This section covers some common issues you might encounter and provides guidance on how to troubleshoot them.

### General Troubleshooting Steps:

1.  **Check Docker Container Logs:** This is almost always the first step. Logs provide detailed error messages and status updates.
    ```bash
    docker logs <container_name_or_id>
    docker logs -f <container_name_or_id> # To follow logs in real-time
    ```
    Replace `<container_name_or_id>` with `overpass_api` or `nominatim_service` (or whatever you named them).

2.  **Check Docker Container Status:** Ensure the containers are running.
    ```bash
    docker ps -a 
    ```
    If a container is exited, the logs (from `docker logs`) should indicate why.

3.  **Check Docker Resources:** Ensure Docker has enough resources (CPU, memory, disk space) allocated if you are running Docker Desktop or have system-wide limits.
    ```bash
    docker stats <container_name_or_id>
    ```

4.  **Verify Port Mappings:** Ensure the ports you mapped in `docker-compose.yml` are not already in use on your host and that you are using the correct host port to access the service.
    ```bash
    sudo netstat -tulnp | grep <port_number>
    ```

5.  **Check Disk Space:** Both Overpass and Nominatim can consume significant disk space, especially during import or if logs grow large.
    ```bash
    df -h
    ```

6.  **Permissions:** Incorrect file/directory permissions on mounted volumes are a common source of problems, especially for database directories.
    *   For Overpass, ensure the directory mounted to `/db` (e.g., `/srv/overpass_db`) is writable by the user ID the Overpass container runs as (often root or a dedicated user).
    *   For Nominatim, the PostgreSQL data directory (e.g., `/srv/nominatim_data` mounted to `/var/lib/postgresql/XX/main`) needs to be writable by the `postgres` user within the container (often UID 999 for `mediagis/nominatim`).

### Overpass API Specific Issues:

1.  **Initial Import Takes Very Long / Seems Stuck:**
    *   **Patience:** Importing data, even for a region, can take time. Monitor logs for progress.
    *   **Resources:** The import process is CPU and I/O intensive. Ensure your server has adequate RAM and fast disk (SSD recommended). If using a VM, ensure it has enough resources allocated.
    *   **PBF File:** Ensure the PBF file is not corrupted and is correctly specified in `OVERPASS_CLONE_FILE`.
    *   **Logs:** Check `docker logs overpass_api` for any specific error messages during `osm-db_clone`.

2.  **Queries Timeout / API Unresponsive:**
    *   **Import Not Complete:** The API will not be responsive until the initial data import is fully complete and the dispatcher is running.
    *   **Server Resources:** Your server might be overloaded. Check CPU/memory usage (`htop`, `docker stats`).
    *   **Query Complexity:** Very complex or broad queries can take a long time. Try simpler queries first.
    *   **Overpass Configuration:** Check `OVERPASS_MAX_TIMEOUT` or similar settings in your Docker environment variables or Overpass configuration files if you did a manual install.
    *   **Dispatcher Not Running:** Ensure the `osm3s_dispatcher` process is running inside the container or on your server (for manual installs).

3.  **Data Not Updating:**
    *   **`OVERPASS_DIFF_URL`:** Verify this environment variable in `docker-compose.yml` points to the correct update URL for your region (from Geofabrik).
    *   **Update Scripts/Cron (Manual Install):** Ensure your update scripts are configured correctly and cron jobs are running without errors.
    *   **Disk Space:** Updates can fail if there isn't enough disk space for new data or temporary files.
    *   **Logs:** Look for errors related to `fetch_osc.sh` or `apply_osc_to_db.sh` in the logs.

4.  **"Area generation" issues or slow `area(...)` queries:**
    *   Overpass API might need to generate area data. This can be a separate step after initial import. Some Docker images might handle this automatically, or you might need to run a command like `osm3s_query --rules --db-dir=/db` (path inside container) after import.

### Nominatim Specific Issues:

1.  **Initial Import Fails or Takes Extremely Long:**
    *   **RAM and Disk I/O:** Nominatim import is extremely demanding on RAM and disk I/O. Insufficient RAM is a very common cause of failure or extreme slowness. For a country like the Netherlands, 16GB RAM is a good minimum, more is better. SSDs are crucial.
    *   **Disk Space:** Ensure ample free disk space (hundreds of GBs for a country, terabytes for planet).
    *   **PBF File:** Corrupted or incomplete PBF file.
    *   **PostgreSQL Issues:** Problems with the PostgreSQL setup within the container. Check `docker logs nominatim_service` for PostgreSQL errors.
    *   **Permissions:** The PostgreSQL data directory on the host (`/srv/nominatim_data`) must be writable by the PostgreSQL user in the container (often UID 999).

2.  **Nominatim API (e.g., `http://localhost:8088`) Not Responding or Gives Errors (e.g., 502 Bad Gateway, 404 Not Found):**
    *   **Import Not Complete:** The web service will likely not function correctly until the full import and indexing process is finished.
    *   **Web Server Configuration (inside container):** The Docker image should handle this, but if you built your own, Apache/Nginx might not be configured correctly to serve Nominatim.
    *   **PostgreSQL Not Running/Accessible:** The Nominatim frontend needs to connect to its PostgreSQL database.
    *   **Container Logs:** Check `docker logs nominatim_service` for errors from Apache/Nginx or PHP, or Nominatim itself.

3.  **Reverse Geocoding Returns No Results or Incorrect Results:**
    *   **Data Import Issues:** The data for the queried area might not have been imported correctly or might be missing.
    *   **Indexing:** Ensure all indexing steps completed successfully during import.
    *   **Nominatim Version/PBF Compatibility:** Ensure your Nominatim version is compatible with the OSM PBF data format and any special tags used.

4.  **Updates Not Working:**
    *   **`REPLICATION_URL`:** Ensure this is correctly set in `docker-compose.yml`.
    *   **Update Process:** The `mediagis/nominatim` image (and others) usually has scripts to handle updates. Check logs for update activity or errors.
    *   **Disk Space/Resources:** Updates also require resources.

### Python Script Connection Issues:

1.  **`ConnectionRefusedError`:**
    *   **Service Not Running:** The Docker container for Overpass or Nominatim might not be running or might have exited due to an error.
    *   **Incorrect IP/Port:** Double-check the IP address and port in your Python script. If running scripts on the same machine as Docker, use `localhost` or `127.0.0.1` and the *host* port you mapped (e.g., `12345` for Overpass, `8088` for Nominatim).
    *   **Firewall:** A firewall on your server might be blocking connections to the mapped ports. Ensure the ports are open.

2.  **Timeout Errors in Python Script:**
    *   **Server Overload:** Your self-hosted instance might be too slow or overloaded.
    *   **Query Too Complex (Overpass):** The query might be too demanding for your server's current configuration or hardware.
    *   **Network Issues:** Less likely for local connections, but possible.
    *   **Increase Timeout in Script:** You can increase the `timeout` parameter in your `requests.post()` or `requests.get()` calls, but also investigate the server-side cause.

### General Advice:

*   **Start Small:** If you are new to this, try importing data for a smaller city or region first to understand the process and resource requirements before attempting a larger country or continent.
*   **Consult Official Documentation:** The official Overpass API and Nominatim websites and their respective Docker image documentation (e.g., on Docker Hub) are valuable resources.
*   **Community Forums:** Websites like the OpenStreetMap help forum (help.openstreetmap.org) or Stack Overflow (tagged with `openstreetmap`, `overpass-api`, `nominatim`) can be useful for searching for solutions to specific error messages.

By systematically checking logs and common points of failure, you can usually diagnose and resolve most issues encountered during setup and operation.
