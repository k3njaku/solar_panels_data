# My Setup:

```
PowerShell Extension v2025.0.0
Copyright (c) Microsoft Corporation.

https://aka.ms/vscode-powershell
Type 'help' to get help.

PS C:\TJ\SolarPan> systeminfo 

Host Name:                 TALHA-JAVED
OS Name:                   Microsoft Windows 10 Pro
OS Version:                10.0.19045 N/A Build 19045
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Workstation
OS Build Type:             Multiprocessor Free
Registered Owner:          Lenovo
Registered Organization:
Product ID:                00330-51181-69926-AAOEM
Original Install Date:     4/11/2023, 6:40:13 AM
System Boot Time:          5/8/2025, 2:47:08 PM
System Manufacturer:       LENOVO
System Model:              20HEA0TLUS
System Type:               x64-based PC
Processor(s):              1 Processor(s) Installed.
                           [01]: Intel64 Family 6 Model 142 Stepping 9 GenuineIntel ~2611 Mhz
BIOS Version:              LENOVO N1QET98W (1.73 ), 12/26/2022
Windows Directory:         C:\WINDOWS
System Directory:          C:\WINDOWS\system32
Boot Device:               \Device\HarddiskVolume1
System Locale:             en-us;English (United States)
Input Locale:              en-us;English (United States)
Time Zone:                 (UTC+05:00) Islamabad, Karachi
Total Physical Memory:     15,987 MB
Available Physical Memory: 7,517 MB
Virtual Memory: Max Size:  23,127 MB
Virtual Memory: Available: 11,395 MB
Virtual Memory: In Use:    11,732 MB
Page File Location(s):     C:\pagefile.sys
Domain:                    WORKGROUP
Logon Server:              \\TALHA-JAVED
Hotfix(s):                 31 Hotfix(s) Installed.
                           [01]: KB5056578
                           [02]: KB5028853
                           [03]: KB5011048
                           [04]: KB5012170
                           [05]: KB5015684
                           [06]: KB5055612
                           [07]: KB5022924
                           [08]: KB5023794
                           [09]: KB5025315
                           [10]: KB5026879
                           [11]: KB5028318
                           [12]: KB5028380
                           [13]: KB5029709
                           [14]: KB5031539
                           [15]: KB5032392
                           [16]: KB5032907
                           [17]: KB5034224
                           [18]: KB5036447
                           [19]: KB5037018
                           [20]: KB5037240
                           [21]: KB5037995
                           [22]: KB5039336
                           [23]: KB5041579
                           [24]: KB5043935
                           [25]: KB5043130
                           [26]: KB5046823
                           [27]: KB5050388
                           [28]: KB5050111
                           [29]: KB5052916
                           [30]: KB5054682
                           [31]: KB5055663
Network Card(s):           2 NIC(s) Installed.
                           [01]: Intel(R) Ethernet Connection (4) I219-LM
                                 Connection Name: Ethernet
                                 Status:          Media disconnected
                           [02]: Intel(R) Dual Band Wireless-AC 8265
                                 Connection Name: Wi-Fi
                                 DHCP Enabled:    Yes
                                 DHCP Server:     192.168.100.1
                                 IP address(es)
                                 [01]: 192.168.100.21
                                 [02]: fe80::dbfd:b76:39cb:5f86
                                 [03]: 2406:d00:cccd:fe2f:c0a:830b:bdb3:5d6c    
                                 [04]: 2406:d00:cccd:fe2f:d7f0:5b55:2f7a:557b   
Hyper-V Requirements:      A hypervisor has been detected. Features required for Hyper-V will not be displayed.
PS C:\TJ\SolarPan> 
```

- Windows 10
    
- VS Code
    
- Github
    
- OSGeo4W Shell (✔ now embedded in VS Code)
    

### What I really need are these:

- **Objectnummer**
    
- **Street**
    
- **Housenumber**
    
- **Postal code**
    
- **City**
    
- **Country**
    
- **Gebruiksdoel**
    
- **Functie**
    
- **Google maps link URL** (📍 next step)
    
- **Longitude LNG**
    
- **Latitude LAT**
    

### Current Task: Google Maps Pin Links ✅

We’re now at the stage where we embed Google Maps URLs using centroid coordinates for each building.

---

### Checkpoint Workflow: Google Maps Pin Links

Break down into granular checkpoints—run each, confirm output, then move on.

**Checkpoint 1: Centroid Extraction & CSV Preview**

```cmd
ogrinfo -ro bag-light.gpkg -sql "SELECT identificatie, ST_X(ST_Centroid(geom)) AS LNG, ST_Y(ST_Centroid(geom)) AS LAT FROM pand LIMIT 5"
```

- ✅ Expect 5 rows of `identificatie`, `LNG`, `LAT` in RD New projection.
    
- ❓ Confirm you see valid numeric values.
    

**Checkpoint 2: Address Fields Preview**

```cmd
ogrinfo -ro bag-light.gpkg -sql "SELECT pand_identificatie, openbare_ruimte_naam AS street, huisnummer, postcode, woonplaats_naam AS city FROM verblijfsobject LIMIT 5"
```

- ✅ Expect 5 address rows matching `pand_identificatie` to buildings.
    
- ❓ Confirm street names, house numbers, and city values.
    

**Checkpoint 3: Merge Preview (RD New)**

```cmd
ogrinfo -ro bag-light.gpkg -sql "SELECT p.identificatie AS Objectnummer, s.street, s.huisnummer, s.postcode, s.city, ST_X(ST_Centroid(p.geom)) AS LNG, ST_Y(ST_Centroid(p.geom)) AS LAT FROM pand p JOIN (SELECT pand_identificatie, openbare_ruimte_naam AS street, huisnummer, postcode, woonplaats_naam AS city FROM verblijfsobject) s ON p.identificatie = s.pand_identificatie LIMIT 5"
```

- ✅ Expect combined 5 rows with all fields in RD New.
    
- ❓ Confirm that `Objectnummer` matches `pand_identificatie`.
    

**Checkpoint 4a: Small Batch Export with Progress**

```cmd
ogr2ogr -f CSV solar_addresses_part.csv -progress -skipfailures -sql "SELECT p.identificatie AS Objectnummer, s.openbare_ruimte_naam AS street, s.huisnummer, s.postcode, s.woonplaats_naam AS city, ST_X(ST_Centroid(p.geom)) AS LNG, ST_Y(ST_Centroid(p.geom)) AS LAT, 'Nederland' AS Country FROM pand p JOIN verblijfsobject s ON p.identificatie = s.pand_identificatie LIMIT 10000" bag-light.gpkg
```

- ✅ Exports first 10k rows into `solar_addresses_part.csv` quickly, showing percentage progress.
    
- ❓ Check file and progress output to confirm speed.
    

**Checkpoint 4b: Full Export with Detailed Logging & Resume**

```cmd
ogr2ogr --verbose -progress -skipfailures -append -f CSV solar_addresses.csv -sql "SELECT p.identificatie AS Objectnummer, s.openbare_ruimte_naam AS street, s.huisnummer, s.postcode, s.woonplaats_naam AS city, ST_X(ST_Centroid(p.geom)) AS LNG, ST_Y(ST_Centroid(p.geom)) AS LAT, 'Nederland' AS Country FROM pand p JOIN verblijfsobject s ON p.identificatie = s.pand_identificatie" bag-light.gpkg >ogr2ogr.log 2>&1
```

- `--verbose` prints detailed internal messages.
    
- `-progress` shows percentage progress.
    
- `-skipfailures` skips problematic features without stopping.
    
- `-append` allows resuming the export if re-run.
    
- Redirection `>ogr2ogr.log 2>&1` captures both output and errors in `ogr2ogr.log`.
    

**Checkpoint 4c: Random Sample Validation**

```cmd
# PowerShell sample 10 random lines (skip header)
powershell -Command "Get-Content solar_addresses.csv | Select-Object -Skip 1 | Get-Random -Count 10"
```

```bash
# Bash (if shuf available)
shuf -n 10 solar_addresses.csv
```

- ✅ This outputs 10 random data rows for quick validity check.
    
- ❓ Confirm that sampled lines have correct Objectnummer, street, postcode, and coordinates.
    

> **Note:** `solar_addresses.csv` does **not** include the `maps_url` column. The Google Maps link URL is generated in **Checkpoint 5** when reprojecting to WGS84.

**Checkpoint 5: Reproject & URL Preview (SQLite Dialect)**

```cmd
ogr2ogr -f CSV solar_addresses_wgs84.csv -dialect sqlite -sql "SELECT Objectnummer, street, huisnummer, postcode, city, Country, ST_X(ST_Transform(MakePoint(LNG, LAT),4326)) AS Longitude, ST_Y(ST_Transform(MakePoint(LNG, LAT),4326)) AS Latitude, 'https://maps.google.com/?q=' || ST_Y(ST_Transform(MakePoint(LNG, LAT),4326)) || ',' || ST_X(ST_Transform(MakePoint(LNG, LAT),4326)) AS maps_url FROM solar_addresses" solar_addresses.csv
```

- **Run this in the OSGeo4W Shell** (so `ogr2ogr` is on PATH).
    
- The `-dialect sqlite` flag enables spatial functions on CSV.
    

> After it finishes, use `head -n 10 solar_addresses_wgs84.csv` (or PowerShell `Get-Content -TotalCount 10`) to verify coordinates and maps URLs.

---

### 📝 Observation & Next Actions

- **Observation:** Running Checkpoint 5 shows the `maps_url` column remains empty.
    
- **Next:** We will debug the SQL syntax or data workflow to correctly populate Google Maps URLs in a later step.
    

# Next steps:

We’ll start by testing the PDOK Zonatlas WFS API in small increments, before downloading full datasets.

#### Step A0: Test WFS Host Connectivity

- **Action:** Check DNS resolution and reachability of the PDOK WFS host.
    
- **Commands (PowerShell):**
    
    ```powershell
    nslookup geodata.nationaalgeoregister.nl
    ping geodata.nationaalgeoregister.nl
    ```
    
- **Goal:** Confirm the host resolves to an IP and is pingable. If these commands fail, your network or DNS is blocking access.
    

#### Step A0b: Manual Download Fallback

- **Action:** If the WFS endpoint is unreachable, manually download the shapefile via browser.
    
- **Instructions:**
    
    1. Open [https://geodata.nationaalgeoregister.nl/solar](https://geodata.nationaalgeoregister.nl/solar) in your browser.
        
    2. Click “Download” and choose **ESRI Shapefile** format.
        
    3. Save `zonnepanelen.zip` into your working directory (`C:\TJ\SolarPan`).
        
- **Goal:** Obtain the shapefile locally without CLI download.
    

#### Step A1: GetCapabilities

- **Action:** Retrieve WFS capabilities with explicit parameters.
    
- **Command:**
    
    ```cmd
    curl "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetCapabilities"
    ```
    
- **Goal:** Inspect available `FeatureTypeList` to confirm the layer name (`zonnepanelen`).
    
- **Action:** Retrieve WFS capabilities with explicit parameters.
    
- **Command:**
    
    ```cmd
    curl "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetCapabilities"
    ```
    
- **Goal:** Inspect available `FeatureTypeList` to confirm the layer name (`zonnepanelen`).
    

#### Step A2: Preview Feature Count

- **Action:** Request a small number of features in JSON to test the query.
    
- **Command:**
    
    ```cmd
    curl "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=zonnepanelen&count=5&outputFormat=application/json"
    ```
    
- **Goal:** Get 5 features back in JSON, verify fields like `id` and `aantal_panelen` exist.
    

#### Step A3: Download Shapefile (ZIP)

- **Action:** Download the full shapefile once endpoint is confirmed.
    
- **Command:**
    
    ```cmd
    curl -L -o zonnepanelen.zip "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=zonnepanelen&outputFormat=shape-zip"
    ```
    
- **Goal:** Obtain `zonnepanelen.zip` for local processing.
    

---

### Local Shapefile Workflow

Once the above tests succeed, proceed with:

**Step B1: Extract & Inspect Layers**

- **Commands:**
    
    ```cmd
    tar -xf zonnepanelen.zip -C zonnepanelen
    ogrinfo zonnepanelen/zonnepanelen.shp -so
    ```
    

**Step B2: Count Intersecting Buildings** ... (unchanged steps)

We’ll download the PDOK “zonnepanelen” layer as a shapefile and then process it locally.

**Step A1: Download Solar Panel Shapefile from PDOK WFS**

- **Action:** Request the `zonnepanelen` layer in ESRI shapefile format.
    
- **Command (CMD / PowerShell):**
    
    ```cmd
    curl -L -o zonnepanelen.zip "http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=zonnepanelen&outputFormat=shape-zip"
    ```
    
- **Goal:** Have `zonnepanelen.zip` containing `zonnepanelen.shp` etc.
    

**Step A2: Extract & Inspect Layers**

- **Action:** Unzip and list layer metadata.
    
- **Commands (CMD / PowerShell):**
    
    ```cmd
    tar -xf zonnepanelen.zip -C zonnepanelen
    ogrinfo zonnepanelen/zonnepanelen.shp -so
    ```
    
- **Goal:** Confirm layer name, geometry type, and key attributes like `id` and `aantal_panelen`.
    

**Step A3: Count Intersecting Buildings**

- **Action:** Count BAG buildings intersecting panel footprints.
    
- **Command:**
    
    ```cmd
    ogrinfo -ro bag-light.gpkg -sql "SELECT COUNT(DISTINCT p.identificatie) AS cnt FROM pand p JOIN zonnepanelen/zonnepanelen.shp s ON ST_Intersects(p.geom, s.geometry)"
    ```
    
- **Goal:** Get approximate count of buildings with panels.
    

**Step A4: Export Panelled Building IDs**

- **Action:** Extract unique BAG IDs of panelled buildings.
    
- **Command:**
    
    ```cmd
    ogr2ogr -f CSV buildings_with_panels.csv -sql "SELECT DISTINCT p.identificatie AS Objectnummer FROM bag-light.gpkg p JOIN zonnepanelen/zonnepanelen.shp s ON ST_Intersects(p.geom, s.geometry)" bag-light.gpkg
    ```
    
- **Goal:** `buildings_with_panels.csv` listing `Objectnummer` of panelled buildings.
    

**Step A5: Merge Panel Info into Address List**

- **Action:** Annotate address CSV with a `has_panels` flag.
    
- **Command (SQLite dialect):**
    
    ```cmd
    ogr2ogr -f CSV solar_addresses_final.csv -dialect sqlite -sql "SELECT a.*, CASE WHEN b.Objectnummer IS NOT NULL THEN 1 ELSE 0 END AS has_panels FROM 'csv/solar_addresses.csv' a LEFT JOIN 'csv/buildings_with_panels.csv' b ON a.Objectnummer = b.Objectnummer" csv
    ```
    
- **Goal:** `solar_addresses_final.csv` with `has_panels` = 1/0 per building.
    

> Run **Step A1** to download and confirm the shapefile, then proceed to **Step A2**.**

- **Action:** Preview the `zonnepanelen` layer from PDOK’s WFS.
    
- **Command (OSGeo4W Shell):**
    
    ```cmd
    ogrinfo WFS:"http://geodata.nationaalgeoregister.nl/solar/ows?service=WFS&version=2.0.0&request=GetCapabilities" zonnepanelen -so
    ```
    

# Note: Use HTTP (not HTTPS) or verify network/DNS connectivity to resolve the PDOK WFS host.

````
- **Goal:** Confirm layer name `zonnepanelen` and geometry (likely polygons representing panel areas).

**Step A2: Sample Panel Features**
- **Action:** Fetch a small sample of solar panel features.
- **Command (OSGeo4W Shell):**
```cmd
ogrinfo WFS:"https://geodata.nationaalgeoregister.nl/solar/ows" -sql "SELECT id, naam, aantal_panelen, geom FROM zonnepanelen LIMIT 5"
````

- **Goal:** Verify attributes such as `id`, `aantal_panelen` and geometry type.
    

**Step A3: Count Intersecting Buildings**

- **Action:** Count how many BAG buildings intersect any panel footprint.
    
- **Command:**
    
    ```cmd
    ogrinfo -ro bag-light.gpkg -sql "SELECT COUNT(DISTINCT p.identificatie) AS cnt FROM pand p JOIN WFS:'https://geodata.nationaalgeoregister.nl/solar/ows' zonnepanelen s ON ST_Intersects(p.geom, s.geom)"
    ```
    
- **Goal:** Get an approximate count of panelled buildings.
    

**Step A4: Export Panelled Building IDs**

- **Action:** Extract unique BAG IDs of buildings with panels.
    
- **Command:**
    
    ```cmd
    ogr2ogr -f CSV buildings_with_panels.csv -sql "SELECT DISTINCT p.identificatie AS Objectnummer FROM bag-light.gpkg p JOIN WFS:'https://geodata.nationaalgeoregister.nl/solar/ows' zonnepanelen s ON ST_Intersects(p.geom, s.geom)" bag-light.gpkg
    ```
    
- **Goal:** Create `buildings_with_panels.csv` listing `Objectnummer` of panelled buildings.
    

**Step A5: Merge Panel Info into Address List**

- **Action:** Annotate your main CSV with a `has_panels` flag.
    
- **Command (SQLite dialect):**
    
    ```cmd
    ogr2ogr -f CSV solar_addresses_final.csv -dialect sqlite -sql "SELECT a.*, CASE WHEN b.Objectnummer IS NOT NULL THEN 1 ELSE 0 END AS has_panels FROM 'csv/solar_addresses.csv' a LEFT JOIN 'csv/buildings_with_panels.csv' b ON a.Objectnummer = b.Objectnummer" csv
    ```
    
- **Goal:** Generate `solar_addresses_final.csv` with buildings flagged (`has_panels` = 1/0).
    

> Run **Step A1** to preview the WFS layer and confirm connectivity, then proceed to **Step A2**.