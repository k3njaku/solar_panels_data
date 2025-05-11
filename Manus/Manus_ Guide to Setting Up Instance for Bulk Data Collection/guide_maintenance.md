## Maintenance and Updates for Self-Hosted Instances

Once your self-hosted Overpass API and Nominatim services are operational, ongoing maintenance is crucial for ensuring their stability, security, and data accuracy. This section outlines key maintenance tasks and how to keep your services and their underlying data updated.

### General Maintenance Practices (for Docker-based setups):

1.  **Monitor Docker Container Health:**
    *   Regularly check the status of your Docker containers:
        ```bash
        docker ps
        ```
    *   Review logs for any persistent errors or warnings:
        ```bash
        docker logs overpass_api
        docker logs nominatim_service
        ```
    *   Monitor resource usage to ensure containers are not consistently hitting limits:
        ```bash
        docker stats
        ```

2.  **Host System Updates:**
    *   Keep your underlying host operating system (e.g., Ubuntu Server) updated with the latest security patches and system updates:
        ```bash
        sudo apt update
        sudo apt upgrade -y
        sudo apt autoremove -y # To remove unused packages
        ```
    *   Reboot the host system if required by kernel updates, ensuring your Docker containers are configured to restart automatically (`restart: unless-stopped` or `restart: always` in `docker-compose.yml`).

3.  **Docker Engine and Docker Compose Updates:**
    *   Periodically update Docker Engine and Docker Compose to their latest stable versions to benefit from new features and security fixes. Follow the official Docker documentation for update procedures.

4.  **Backup Persistent Data:**
    *   **Crucial:** Regularly back up the persistent data volumes used by your Overpass and Nominatim containers.
        *   **Overpass Data:** The directory mapped to `/db` (e.g., `/srv/overpass_db`).
        *   **Nominatim Data:** The PostgreSQL data directory mapped (e.g., `/srv/nominatim_data`).
    *   The backup strategy depends on your environment. You can use tools like `rsync`, `tar`, or dedicated backup solutions. Ensure containers are stopped or databases are properly shut down/quiesced during backup if live backups are not supported by the specific database technology without risk of corruption.
        *   Example (simple tar backup, stop containers first for safety):
            ```bash
            # In your docker-compose directory
            docker-compose stop overpass nominatim # Or individual service names
            sudo tar -czvf /backup_location/overpass_db_backup_$(date +%Y%m%d).tar.gz /srv/overpass_db
            sudo tar -czvf /backup_location/nominatim_data_backup_$(date +%Y%m%d).tar.gz /srv/nominatim_data
            docker-compose start overpass nominatim
            ```
        *   For PostgreSQL (Nominatim), more robust backup methods like `pg_dumpall` or `pg_basebackup` can be used, potentially by exec-ing into the Nominatim container or connecting to the database if exposed.

5.  **Manage Disk Space:**
    *   Monitor disk space on your host system, especially for the volumes storing OSM data, database files, and Docker images/logs.
        ```bash
        df -h
        docker system df # Shows Docker disk usage
        ```
    *   Clean up unused Docker images, containers, volumes, and networks periodically:
        ```bash
        docker system prune -a # Use with caution, removes all unused items
        docker image prune
        docker container prune
        docker volume prune
        ```

### Updating Overpass API and Nominatim Software (Docker Images):

Using Docker images simplifies software updates. You generally pull a newer version of the image and recreate the container.

1.  **Check for New Image Versions:**
    *   Periodically visit Docker Hub (or the image provider's repository) for the Overpass API image (e.g., `wiktorn/overpass-api`) and Nominatim image (e.g., `mediagis/nominatim`) to see if new versions or tags are available.

2.  **Update Process using `docker-compose`:**
    *   **Backup Data First:** Always back up your persistent data volumes before attempting a software update.
    *   **Update `docker-compose.yml`:** If you specified a version tag (e.g., `mediagis/nominatim:4.3`), update it to the new desired version (e.g., `mediagis/nominatim:4.4`). If you used `latest`, it will attempt to pull the newest `latest` tag.
    *   **Pull the New Image:**
        ```bash
        # In your docker-compose directory
        docker-compose pull overpass # Or your Overpass service name
        docker-compose pull nominatim # Or your Nominatim service name
        ```
    *   **Stop and Recreate Containers:**
        ```bash
        docker-compose down # Stops and removes containers, but not volumes by default
        docker-compose up -d # Recreates containers with the new image and existing volumes
        ```
    *   **Monitor Logs:** After recreating, check the logs to ensure the services start correctly with the new version and that your data is intact and accessible.
    *   **Database Migrations:** For Nominatim, if there are database schema changes between versions, the new Docker image might attempt to run migration scripts. This is a critical phase; monitor logs closely. Major version upgrades might have specific instructions from the image maintainer.

### Updating OpenStreetMap Data:

Keeping your local OSM data up-to-date is essential for accurate results.

*   **Overpass API (Docker - `wiktorn/overpass-api`):**
    *   If you configured `OVERPASS_DIFF_URL` in your `docker-compose.yml`, the container usually has internal mechanisms (cron jobs running scripts like `fetch_osc.sh` and `apply_osc_to_db.sh`) to automatically download and apply daily or hourly updates from the specified Geofabrik replication service.
    *   **Verification:** Check the container logs for messages related to these update scripts. You should see activity indicating diffs are being fetched and applied.
    *   **Manual Trigger (if needed):** While usually automatic, some images might provide a way to manually trigger an update cycle, or you might need to restart the container for it to pick up a missed cycle (less ideal).

*   **Nominatim (Docker - `mediagis/nominatim`):**
    *   Similarly, if `REPLICATION_URL` is set, the `mediagis/nominatim` image typically includes scripts to periodically update the database with OSM diffs.
    *   **Verification:** Check container logs for update activity (e.g., messages from `nominatim replication` or similar tools).
    *   The environment variable `NOMINATIM_MODE: "update"` might be relevant after the initial import to ensure it focuses on applying updates.
    *   **Replication Lag:** Be aware that replication can sometimes lag. You can often check the timestamp of the last applied update by querying the database or checking specific status files (methods vary by image).

*   **Manual Installation Data Updates:**
    *   If you installed manually, you are responsible for setting up and maintaining cron jobs that run the Overpass API update scripts (`fetch_osc.sh`, `apply_osc_to_db.sh`, etc.) or Nominatim's update tools (`nominatim replication ...`).
    *   Ensure these cron jobs are running correctly and that the state files (which track the last applied sequence number) are properly managed.

**Full Re-import vs. Incremental Updates:**

*   Incremental updates are generally efficient for keeping data current.
*   However, if your data becomes very old, or if you suspect corruption, or if there are major changes in the OSM data processing tools, a full re-import from a fresh PBF file might occasionally be necessary. This is a longer process but ensures a clean state.

### Security Considerations:

*   **Firewall:** Ensure your host server's firewall is configured to only expose the necessary ports (e.g., the host ports you mapped for Overpass and Nominatim APIs, and SSH for server management). Do not expose database ports directly to the internet unless absolutely necessary and properly secured.
*   **Limit Access:** If your services don't need to be public, restrict access to specific IP ranges or use a reverse proxy with authentication.
*   **Docker Security:** Follow Docker security best practices (e.g., run containers as non-root where possible, keep Docker updated, use trusted images).

By following these maintenance and update procedures, you can ensure your self-hosted Overpass API and Nominatim instances remain reliable, secure, and provide you with up-to-date OpenStreetMap data for your projects.
