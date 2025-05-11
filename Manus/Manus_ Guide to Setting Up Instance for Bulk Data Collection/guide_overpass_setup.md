## Setting up a Self-Hosted Overpass API Instance

This section will guide you through setting up your own Overpass API instance. We will cover two main approaches: using Docker (recommended for ease of setup and management) and a manual installation from source. We will also discuss how to import data for a specific region, such as the Netherlands, which is relevant to your project.

### Option 1: Installation using Docker (Recommended)

Using Docker simplifies the installation process significantly by packaging the Overpass API and its dependencies into a container. There are several community-maintained Docker images for Overpass API. A popular one is from `wiktorn/overpass-api`.

**1. Install Docker and Docker Compose:**

If you haven't already, install Docker and Docker Compose on your Ubuntu server. You can find the latest official instructions on the Docker website:

*   Install Docker Engine: [https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/)
*   Install Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

Verify the installations:
```bash
docker --version
docker-compose --version # or docker compose version for newer installations
```

**2. Prepare Data Directory and Download OSM Data:**

First, create a directory on your host system where the Overpass database will be stored. This allows the data to persist even if the Docker container is removed or updated.

```bash
# Choose a location with sufficient disk space (e.g., /opt/overpass_db or /srv/overpass_db)
# For this guide, we'll use /srv/overpass_db
sudo mkdir -p /srv/overpass_db
sudo chown $(whoami):$(whoami) /srv/overpass_db # Or adjust permissions as needed
```

Next, download the OpenStreetMap data extract for the region you need. For the Netherlands, you can get it from Geofabrik:

*   Go to [https://download.geofabrik.de/europe/netherlands.html](https://download.geofabrik.de/europe/netherlands.html)
*   Download the `.osm.pbf` file (e.g., `netherlands-latest.osm.pbf`).

Place this file in a directory accessible to Docker, for example, create a temporary data directory:

```bash
mkdir ~/osm_data
wget -P ~/osm_data https://download.geofabrik.de/europe/netherlands-latest.osm.pbf
# Note: The exact URL might change, always check Geofabrik for the latest link.
```

**3. Create a `docker-compose.yml` file:**

Create a file named `docker-compose.yml` in a new directory (e.g., `~/overpass-docker/`) with the following content. This configuration will download the Overpass API image, set up the necessary volumes, and initialize the database with your chosen OSM extract.

```yaml
version: "3.8"

services:
  overpass:
    image: wiktorn/overpass-api:latest
    container_name: overpass_api
    ports:
      - "12345:80"  # Exposes Overpass API on host port 12345, container port 80
    volumes:
      - /srv/overpass_db:/db # Mounts the persistent database directory
      - ~/osm_data:/osm_data # Mounts the directory with your OSM PBF file
    environment:
      # OVERPASS_META: "no" # Set to "yes" to include metadata (larger db, more features)
      OVERPASS_MODE: "clone" # Use "clone" for initial setup with a PBF file
      OVERPASS_CLONE_FILE: "/osm_data/netherlands-latest.osm.pbf" # Path inside the container
      OVERPASS_DIFF_URL: "https://download.geofabrik.de/europe/netherlands-updates/" # For updates
      OVERPASS_RULES_LOAD: 10 # Number of threads for initial data load
      OVERPASS_MAX_TIMEOUT: 1000 # Optional: Increase max query timeout (seconds)
      # OVERPASS_RATE_LIMIT: 1000 # Optional: Queries per minute (default is usually high for local)
      # OVERPASS_SPACE_LIMIT: 2000000000 # Optional: Max memory for a query in bytes (e.g., 2GB)
    restart: unless-stopped
    # For initial import, you might want to allocate more resources if available
    # mem_limit: 8g # Example: limit memory to 8GB
    # cpus: 4       # Example: limit to 4 CPUs

# Optional: Add a simple Nginx reverse proxy if you want to access it via a standard port (80/443)
# or add SSL. For initial setup, direct port mapping is fine.
```

**Important Notes for `docker-compose.yml`:**

*   **`ports`**: `"12345:80"` maps port `12345` on your host machine to port `80` inside the Docker container where the Overpass API service (usually Apache or Nginx within the container) listens. You can choose any available host port instead of `12345`.
*   **`volumes`**: `/srv/overpass_db:/db` ensures your database is stored outside the container. `~/osm_data:/osm_data` makes your downloaded PBF file available to the container.
*   **`OVERPASS_CLONE_FILE`**: Make sure this path matches where you mounted your OSM data and the filename.
*   **`OVERPASS_DIFF_URL`**: This is crucial for keeping your database updated. Find the correct URL for your region on Geofabrik (usually in the `-updates` subdirectory).
*   **Resource Allocation (`mem_limit`, `cpus`):** The initial import of OSM data is resource-intensive. If you have ample RAM and CPU, uncommenting and adjusting these lines can speed up the process. For a Netherlands-sized extract, 8GB RAM and 4 CPUs should be a good starting point if available.

**4. Start the Overpass API Instance:**

Navigate to the directory where you saved your `docker-compose.yml` file and run:

```bash
docker-compose up -d
```

This command will download the Docker image (if not already present) and start the container in detached mode (`-d`).

**5. Monitor the Initial Data Import:**

The first time you start the container, it will begin importing the OSM data from your PBF file. This process can take a significant amount of time, from minutes for a small city to many hours or even days for a full planet (though for the Netherlands, expect it to be in the range of tens of minutes to a few hours, depending on your hardware).

You can monitor the progress by checking the container's logs:

```bash
docker-compose logs -f overpass
```

Look for messages indicating the progress of `osm-db_clone` or similar processes. You will see messages about reading nodes, ways, and relations. The process is complete when the dispatcher starts and the API becomes responsive.

**6. Test Your Self-Hosted Overpass API:**

Once the import is complete and the logs indicate the service is running (e.g., you see messages from `osm3s_query` or Apache/Nginx access logs), you can test it. The API endpoint will be `http://YOUR_SERVER_IP:12345/api/interpreter`.

You can use `curl` or a browser to send a simple query. For example, to find cafes in a small bounding box (adjust coordinates for the Netherlands):

```bash
curl -X POST -d \
"[out:json];
node(52.0,4.0,52.1,4.1)[amenity=cafe];
out body;" \
http://YOUR_SERVER_IP:12345/api/interpreter
```

Replace `YOUR_SERVER_IP` with the IP address of your server. If you are running this on your local machine, you can use `localhost` or `127.0.0.1`.

**7. Keeping the Data Updated:**

The Docker image `wiktorn/overpass-api` is usually configured to automatically fetch and apply daily or hourly diffs from the `OVERPASS_DIFF_URL` you specified. You can check the logs for messages related to `osm-db_diff_import` or `fetch_osc.sh` to see if updates are being applied.

### Option 2: Manual Installation (More Complex)

Manual installation gives you more control but is significantly more complex and error-prone. It involves compiling the Overpass API software (osm-3s) from source and configuring all its components.

**General Steps for Manual Installation (refer to official Overpass API documentation for specifics):**

1.  **Install Prerequisites:** As listed in the "Prerequisites" section (C++ compiler, Expat, zlib, lz4, build tools).
    ```bash
    sudo apt update
    sudo apt install -y g++ make libexpat1-dev zlib1g-dev liblz4-dev libbz2-dev wget git autoconf automake libtool
    ```

2.  **Download Overpass API Source Code:**
    Get the latest stable release from the official Overpass API development site (e.g., `dev.overpass-api.de`) or clone the Git repository.
    ```bash
    # Example for a specific version, check for the latest
    wget http://dev.overpass-api.de/releases/osm-3s_vX.Y.Z.tar.gz
    tar -xvf osm-3s_vX.Y.Z.tar.gz
    cd osm-3s_vX.Y.Z
    ```
    Or using git (for a more recent, potentially less stable version):
    ```bash
    git clone https://github.com/drolbr/Overpass-API.git --recursive
    cd Overpass-API
    ```

3.  **Configure and Compile:**
    Run the configure script and compile the software. You'll need to specify an installation directory (`$EXEC_DIR`) and a database directory (`$DB_DIR`).
    ```bash
    # Define your directories
    export EXEC_DIR="/opt/osm-3s/osm-3s_vX.Y.Z"
    export DB_DIR="/srv/overpass_db_manual"
    sudo mkdir -p $EXEC_DIR $DB_DIR
    sudo chown -R $(whoami):$(whoami) $EXEC_DIR $DB_DIR

    # For source from tarball
    ./configure CXXFLAGS="-O2" --prefix=$EXEC_DIR
    make
    sudo make install

    # For source from git (might require autogen.sh first)
    # ./autogen.sh
    # ./configure CXXFLAGS="-O2" --prefix=$EXEC_DIR
    # make
    # sudo make install
    ```

4.  **Populate the Database:**
    Download your OSM data extract (e.g., `netherlands-latest.osm.pbf`). You'll need `osmconvert` to convert PBF to OSM XML if your Overpass version doesn't directly support PBF for population (older versions might not).
    ```bash
    # If needed, install osmconvert
    sudo apt install osmctools

    # Convert PBF to OSM XML (if your Overpass version requires it)
    osmconvert ~/osm_data/netherlands-latest.osm.pbf -o=~/osm_data/netherlands-latest.osm

    # Populate the database (this command might vary based on Overpass version)
    # Ensure $DB_DIR is set and writable
    # The init_osm3s.sh script is usually part of the source distribution
    # It might take a planet file or an extract as input.
    # Example (syntax can vary, check your Overpass version's documentation):
    $EXEC_DIR/bin/init_osm3s.sh ~/osm_data/netherlands-latest.osm $DB_DIR $EXEC_DIR
    # Or, if it supports PBF directly for population:
    # $EXEC_DIR/bin/osm3s_query --db-dir=$DB_DIR --load-pbf=~/osm_data/netherlands-latest.osm.pbf
    ```
    This step is highly specific to the version of Overpass API you are installing. **Consult the official documentation that comes with your downloaded source code.**

5.  **Set up Update Process:**
    To keep your database updated, you'll need to configure scripts to download and apply diff files (e.g., minutely, hourly, or daily updates from Geofabrik). This typically involves scripts like `fetch_osc.sh` and `apply_osc_to_db.sh` found in the Overpass source (`$EXEC_DIR/etc/`). You'll need to set up cron jobs to run these scripts regularly.
    ```bash
    # Example: Create a directory for replication data
    export REPLICATE_DIR="/srv/overpass_replicate"
    sudo mkdir -p $REPLICATE_DIR
    sudo chown -R $(whoami):$(whoami) $REPLICATE_DIR

    # Configure the update scripts (e.g., by editing $EXEC_DIR/etc/rules/osm_update_time.sh)
    # and set up a cron job.
    ```

6.  **Set up the Web API (Dispatcher and CGI):**
    You'll need to run the Overpass dispatcher daemon (`osm3s_dispatcher`) and configure a web server (like Apache or Nginx) with a CGI script (`overpass_cgi`) to handle API requests.

    *   **Start the dispatcher:**
        ```bash
        nohup $EXEC_DIR/bin/osm3s_dispatcher --osm-base --db-dir=$DB_DIR --meta & 
        ```
    *   **Configure Apache/Nginx:** This involves setting up a CGI handler. An example Apache configuration might look like:
        ```apache
        <Directory "$EXEC_DIR/cgi-bin">
            AllowOverride None
            Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
            Require all granted
            AddHandler cgi-script .cgi
        </Directory>
        ScriptAlias /api/ $EXEC_DIR/cgi-bin/
        ```
        This is a simplified example. Refer to the Overpass API documentation for detailed web server configuration.

**Why Manual Installation is Complex:**

*   Dependency management can be tricky.
*   Compilation can fail on different systems or with different library versions.
*   Setting up the database population, update scripts, and web server integration requires careful configuration of many components.
*   Troubleshooting is often more involved.

**For these reasons, the Docker approach is strongly recommended, especially if you are not deeply familiar with Linux system administration and software compilation.**

### Data Import and Updates for a Specific Region (e.g., Netherlands)

Whether using Docker or a manual setup, the process for handling regional data involves:

1.  **Initial Import:**
    *   Download the PBF extract for your region (e.g., `netherlands-latest.osm.pbf` from Geofabrik).
    *   During the setup (Docker `OVERPASS_CLONE_FILE` or manual population script), point the Overpass instance to this file.
    *   The initial import will create the database specifically for this region.

2.  **Setting up Updates:**
    *   Find the replication service URL for your region on Geofabrik (e.g., `https://download.geofabrik.de/europe/netherlands-updates/`).
    *   **Docker:** Provide this URL in the `OVERPASS_DIFF_URL` environment variable.
    *   **Manual:** Configure your update scripts (`fetch_osc.sh`, `apply_osc_to_db.sh`) to use this URL and the correct sequence state file location.
    *   Ensure the update process runs regularly (e.g., via cron job for manual setup; Docker images often handle this internally).

By using a regional extract, you significantly reduce the disk space, RAM, and processing time required compared to a full planet import, making it much more feasible for typical server hardware.

### Configuration Details (Key Aspects)

Regardless of the installation method, some key configuration aspects to be aware of (often managed via environment variables in Docker or config files in manual setups):

*   **Database Directory:** The location where the Overpass database is stored. Ensure it has enough space and good I/O performance (SSD recommended).
*   **Update Source URL:** The URL for fetching OSM diffs to keep your data current.
*   **Memory Limits/Timeouts:** For queries, you might need to adjust maximum memory allocation per query or maximum query execution time, especially if you plan to run very large or complex queries. Public instances have strict limits; your own instance can be more generous if your hardware allows.
*   **Rate Limiting:** While you control your own instance, you might still want to configure rate limiting if the API will be accessed by multiple users/scripts to prevent accidental overload.
*   **Area Generation:** Overpass API can precalculate areas (like administrative boundaries) to speed up `area(...)` queries. This might require specific commands or configurations after the initial data import.

For Docker, these are typically set using environment variables in your `docker-compose.yml`. For manual setups, you'd modify configuration files or command-line arguments for the various Overpass components.

In the next section, we will cover setting up a self-hosted Nominatim instance for geocoding.
