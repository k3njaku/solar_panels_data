## Setting up a Self-Hosted Nominatim Instance for Geocoding

This section will guide you through setting up your own Nominatim instance. Nominatim is a tool to search OSM data by name and address (geocoding) and to generate synthetic addresses of OSM points (reverse geocoding). Similar to the Overpass API setup, this can be complex, but having a local instance can be very beneficial for projects requiring extensive geocoding or reverse geocoding lookups without hitting public API limits.

We will primarily focus on a Docker-based setup, as it's generally more straightforward. Manual installation is possible but requires significant Linux administration and PostgreSQL/PostGIS expertise.

### Option 1: Installation using Docker (Recommended)

Using Docker containers simplifies the deployment of Nominatim and its dependencies.

**1. Install Docker and Docker Compose (if not already done):**

Refer to the instructions in the Overpass API setup section if you haven't installed Docker and Docker Compose on your Ubuntu server.

**2. Prepare Data Directory and Download OSM Data:**

Nominatim requires OSM data in PBF format. You will also need a directory on your host system for Nominatim's PostgreSQL database.

```bash
# Create a directory for Nominatim's PostgreSQL data
sudo mkdir -p /srv/nominatim_data
sudo chown -R 999:999 /srv/nominatim_data # Nominatim Docker often runs as user 999

# Create a directory for the PBF file if you don't have one
mkdir -p ~/osm_data_nominatim # Or use the same as Overpass if appropriate

# Download the PBF extract for your region (e.g., Netherlands)
# Example: wget -P ~/osm_data_nominatim https://download.geofabrik.de/europe/netherlands-latest.osm.pbf
# Ensure you have the PBF file (e.g., netherlands-latest.osm.pbf) in this directory.
```
For this example, let's assume `netherlands-latest.osm.pbf` is in `~/osm_data_nominatim/`.

**3. Create a `docker-compose.yml` file for Nominatim:**

Create a file named `docker-compose.yml` (or add to an existing one if you are managing multiple services) in a directory like `~/nominatim-docker/`. Here's an example configuration using the `mediagis/nominatim` image, which is a commonly used one. Adjust paths and versions as needed.

```yaml
version: "3.8"

services:
  nominatim:
    image: mediagis/nominatim:4.3 # Check for the latest stable version
    container_name: nominatim_service
    ports:
      - "8088:8080" # Host port:Container port for Nominatim's web interface
    volumes:
      - /srv/nominatim_data:/var/lib/postgresql/14/main # Mount for PostgreSQL data persistence
      - ~/osm_data_nominatim:/data # Mount for the PBF file
    environment:
      PBF_PATH: "/data/netherlands-latest.osm.pbf" # Path to PBF inside container
      REPLICATION_URL: "https://download.geofabrik.de/europe/netherlands-updates/" # For updates
      # IMPORT_WIKIPEDIA: "true" # Uncomment to import Wikipedia importance scores (optional)
      # NOMINATIM_MODE: "update" # After initial import, can be set to update
      # THREADS: 4 # Number of threads for import, adjust based on your CPU cores
    restart: unless-stopped
    # Add resource limits if necessary, similar to the Overpass example
    # mem_limit: 16g 
    # cpus: 4
```

**Important Notes for `docker-compose.yml`:**

*   **Image Version:** Always check Docker Hub (or the image provider's page) for the latest recommended stable version of the Nominatim image (e.g., `mediagis/nominatim`). Version `4.3` is used as an example.
*   **Ports:** `"8088:8080"` maps port `8088` on your host to port `8080` inside the container where Nominatim's web service (often served by Apache or Nginx within the image) will listen. You can choose a different host port if `8088` is in use.
*   **Volumes:** `/srv/nominatim_data:/var/lib/postgresql/14/main` maps the host directory for PostgreSQL data to the expected location within the container. The internal path `/var/lib/postgresql/14/main` might vary slightly depending on the PostgreSQL version used by the Docker image. You might need to inspect the image or its documentation for the exact path if you encounter issues. `~/osm_data_nominatim:/data` maps your PBF data directory.
*   **`PBF_PATH`**: This tells Nominatim where to find the OSM data *inside* the container. So, it should be `/data/your-file-name.osm.pbf`.
*   **`REPLICATION_URL`**: Similar to Overpass, this is for keeping the data updated. Use the appropriate Geofabrik URL for your region's updates.
*   **`THREADS`**: Adjust based on your server's CPU cores to potentially speed up the import.
*   **`IMPORT_WIKIPEDIA`**: Optional, for better search ranking based on Wikipedia importance.
*   **Permissions for `nominatim_data`**: The PostgreSQL server inside the Docker container will need write access to the mounted volume. The `mediagis/nominatim` image often runs PostgreSQL as a non-root user (e.g., `postgres`, uid `999`). `sudo chown -R 999:999 /srv/nominatim_data` (or the appropriate UID/GID for the postgres user in the container) might be necessary on the host before starting, if you encounter permission errors during database initialization.

**4. Start the Nominatim Service (Initial Import):**

Navigate to the directory where you saved your `docker-compose.yml` file and run:

```bash
docker-compose up -d
```

The first time you run this, Nominatim will start importing the PBF data. This is a **very long process**, potentially taking many hours or even days depending on the size of the PBF file and your hardware. For a country like the Netherlands, expect several hours at least.

You can monitor the progress by looking at the Docker logs:

```bash
docker logs -f nominatim_service 
```
(Or whatever you named your container/service in the `docker-compose.yml`). You should see messages related to database setup, indexing, etc.

**5. Testing the Nominatim API:**

Once the import is complete and the service is running, you can test it. Nominatim typically exposes a search API. The exact URL will depend on the Docker image's internal web server configuration, but it's often on the root or a path like `/search`.

If you mapped port `8088` on the host to the container's port `8080` (or whatever the Nominatim image uses for its web service), you should be able to access it via `http://YOUR_SERVER_IP:8088`.

For example, to search for 
