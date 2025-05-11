# Project Todo List

## Task: Collect Building Data with Solar Panels in North Holland

**Objective:** Provide Python scripts to collect specified building details for structures with solar panels in North Holland using OpenStreetMap and Overpass API.

**Required Fields (from user image):**

*   [ ] Objectnummer
*   [ ] Street
*   [ ] Housenumber
*   [ ] Postal code
*   [ ] City
*   [ ] Country
*   [ ] Gebruiksdoel
*   [ ] Functie (low priority)
*   [ ] Google maps link URL
*   [ ] Longtitude LNG
*   [ ] Latidtude LAT

**Plan Steps:**

1.  [ ] **Analyze Required Building Attributes:** Identify and list all data fields required as per the user-provided image. (Done - listed above)
2.  [ ] **Research OpenStreetMap (OSM) and Overpass API Capabilities:** Investigate if OSM and Overpass API can provide data for the required fields, specifically for buildings with solar panels in North Holland. Focus on tags related to solar installations (e.g., `generator:source=solar`, `power=generator`, `generator:output:electricity=*`, `roof:material=solar_panels`, etc.) and address components.
3.  [ ] **Test Overpass API for North Holland Solar Panel Buildings:** Formulate and execute test queries using the Overpass API (e.g., via Overpass Turbo or a Python script) to retrieve a sample of buildings with solar panels in North Holland. Assess the availability and structure of the returned data.
4.  [ ] **Evaluate Data Coverage for Required Fields:** Compare the data retrieved from the Overpass API against the list of required fields. Determine which fields can be reliably populated and identify any gaps.
    *   [ ] Objectnummer: Check if OSM IDs or other unique identifiers can serve this purpose.
    *   [ ] Street, Housenumber, Postal code, City, Country: Check `addr:*` tags.
    *   [ ] Gebruiksdoel: Check tags like `building=*`, `amenity=*`, `shop=*`, etc.
    *   [ ] Google Maps Link URL: This will likely need to be constructed using latitude and longitude.
    *   [ ] Longitude LNG, Latitude LAT: These are standard OSM data points.
5.  [ ] **Write Python Script for Data Collection:** Develop a Python script that:
    *   [ ] Takes North Holland as the area of interest.
    *   [ ] Queries the Overpass API for buildings with solar panels.
    *   [ ] Parses the API response.
    *   [ ] Extracts the required data fields for each building.
    *   [ ] Handles potential missing data or variations in tagging.
    *   [ ] Constructs the Google Maps link URL from coordinates.
    *   [ ] Outputs the data into a structured format (e.g., CSV, Excel). Consider using the `pandas` library for data manipulation and output.
6.  [ ] **Validate Script Speed and Accuracy:**
    *   [ ] Test the script with a significant portion of North Holland to assess its speed.
    *   [ ] Manually verify a sample of the collected data for accuracy against OSM or other sources if possible.
    *   [ ] Optimize the script for performance if necessary (e.g., efficient querying, batch processing).
7.  [ ] **Report Findings and Send Scripts to User:**
    *   [ ] Summarize the findings, including the feasibility of populating each field and any limitations.
    *   [ ] Provide the Python script(s) as an attachment.
    *   [ ] Include instructions on how to run the script and any dependencies.
