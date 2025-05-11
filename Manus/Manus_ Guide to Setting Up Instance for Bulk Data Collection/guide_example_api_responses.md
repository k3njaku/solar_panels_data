## Example API Responses from Self-Hosted Instances

This section provides an overview of the expected structure of API responses you would receive from your self-hosted Overpass API and Nominatim instances. Understanding these structures is helpful for debugging your scripts and processing the data.

### Overpass API Example Response (JSON)

When you query your self-hosted Overpass API (e.g., using a POST request to `http://YOUR_SERVER_IP:12345/api/interpreter` with a query specifying `[out:json];`), you will receive a JSON response. The structure will be identical to that of the public Overpass API.

**Example Query (Conceptual - finding cafes):**

```
[out:json][timeout:60];
node(52.37, 4.89, 52.38, 4.90)["amenity"="cafe"];
out body;
```

**Example JSON Response Structure:**

```json
{
  "version": 0.6,
  "generator": "Overpass API 0.7.XX YOUR_VERSION_HERE", // Version will reflect your instance
  "osm3s": {
    "timestamp_osm_base": "2023-10-26T12:00:00Z", // Timestamp of your OSM data
    "copyright": "The data included in this document is from www.openstreetmap.org. The data is made available under ODbL."
  },
  "elements": [
    {
      "type": "node",
      "id": 123456789,
      "lat": 52.375,
      "lon": 4.895,
      "tags": {
        "amenity": "cafe",
        "name": "Example Cafe",
        "cuisine": "coffee_shop"
        // ... other tags ...
      }
    },
    {
      "type": "way",
      "id": 987654321,
      "nodes": [
        234567890,
        234567891,
        234567892
        // ... node IDs forming the way ...
      ],
      "tags": {
        "building": "yes",
        "generator:source": "solar",
        "name": "Solar Building Example"
        // ... other tags ...
      }
      // If you requested geometry for ways (e.g., using `out geom;` or `out center;`)
      // you might also get a "geometry" array for ways (list of lat/lon for nodes)
      // or a "center" object with lat/lon.
    }
    // ... more elements ...
  ]
}
```

**Key points for Overpass API responses:**

*   **`elements` array:** This is the main part containing the OSM data (nodes, ways, relations) that match your query.
*   **`type`**: Indicates if the element is a `node`, `way`, or `relation`.
*   **`id`**: The OpenStreetMap ID of the element.
*   **`lat`, `lon`**: Coordinates for nodes.
*   **`nodes` (for ways):** An array of node IDs that make up the way.
*   **`tags`**: A key-value object containing the OSM tags associated with the element.
*   The `version`, `generator`, and `timestamp_osm_base` will reflect your local instance and its data.

Your Python scripts (like `collect_solar_data_geocoded.py`) parse this JSON to extract the IDs, tags, and geometry information.

### Nominatim API Example Response (Reverse Geocoding - JSON)

When you query your self-hosted Nominatim instance for reverse geocoding (e.g., a GET request to `http://YOUR_SERVER_IP:8088/reverse?format=jsonv2&lat=<latitude>&lon=<longitude>`), you will receive a JSON response. The structure is standardized by Nominatim.

**Example Request URL (Conceptual):**

`http://YOUR_SERVER_IP:8088/reverse?format=jsonv2&lat=52.2616747&lon=4.6203717&addressdetails=1&accept-language=nl`

**Example JSON Response Structure:**

```json
{
  "place_id": 1234567,
  "licence": "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
  "osm_type": "way", // or "node", "relation"
  "osm_id": 48595191,
  "lat": "52.2616747",
  "lon": "4.6203717",
  "place_rank": 30, // Importance rank
  "category": "building",
  "type": "school",
  "importance": 0.4,
  "addresstype": "building",
  "name": "Name of the School (if available)",
  "display_name": "Name of the School, 11, Kalslagerring, Nieuw-Vennep, Haarlemmermeer, Noord-Holland, Nederland, 2151 TA, Nederland",
  "address": {
    "amenity": "Name of the School (if available)", // Or other primary feature name
    "road": "Kalslagerring",
    "house_number": "11",
    "suburb": "Nieuw-Vennep West", // If applicable
    "village": "Nieuw-Vennep", // Or city, town, municipality
    "municipality": "Haarlemmermeer",
    "county": "Noord-Holland", // Or state_district
    "state": "Noord-Holland",
    "ISO3166-2-lvl4": "NL-NH",
    "postcode": "2151 TA",
    "country": "Nederland",
    "country_code": "nl"
  },
  "boundingbox": [
    "52.2615747",
    "52.2617747",
    "4.6202717",
    "4.6204717"
  ]
}
```

**Key points for Nominatim reverse geocoding responses:**

*   **`address` object:** This is the most important part for your scripts. It contains the structured address components like `road`, `house_number`, `village`/`city`, `postcode`, `country`, etc.
*   **`display_name`**: A full, human-readable address string.
*   **`osm_type` and `osm_id`**: Link back to the original OSM element if the point falls directly on one.
*   The exact fields present in the `address` object can vary depending on the location and the level of detail in OSM data for that area.
*   Your `get_address_from_coords` function in `collect_solar_data_geocoded.py` is designed to parse this `address` object to fill in missing address fields.

By familiarizing yourself with these response structures, you can better adapt your Python scripts to handle the data returned by your self-hosted services and troubleshoot any discrepancies or parsing issues.
