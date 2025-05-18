# North Holland Solar Data v6:

*What am I even doing?*  
Trying to get a clean CSV of all buildings in North Holland with solar panels, filling out stuff like addresses, Dutch fields, and Google Maps links without losing my focus or patience.

Link to the repo: https://github.com/k3njaku/solar_panels_data
---

## 🟢 Overpass, Python & CSV Dreams

- Started by pulling solar panel features from OpenStreetMap with Overpass Turbo.  
- Played with queries like `node["power"="generator"]["generator:source"="solar"]` and got some decent GeoJSON output.
- Decided on my must-have columns: objectnummer, straatnaam, huisnummer, postcode, woonplaats, land, gebruiksdoel, functie, Google Maps link, and coordinates.
- Quickly realized those Dutch fields (“gebruiksdoel” and “functie”) are not coming from Overpass or normal geocoders. *Yay, more work.*

---

## 🟢 Reverse Geocoding via Python

- Tried using Python scripts with the PDOK API to fill address details.  
- Some scripts worked, others threw annoying network errors (socket.gaierror classic).
- Not sure if I wanna keep fighting with Python or just hop into QGIS and use some plugins to fill the rest.

---

## 🟢 Wrestling with QGIS

- Got myself tangled up in QGIS panels, but figured out how to restore them (double-click the Layers bar, or View > Panels > Layers Panel if I nuke it by accident).
- Installed the PDOK Services plugin and made sure it’s actually working.
- Loaded in the North Holland boundary shapefile/GeoJSON felt proud for about two seconds.
- Added the Zon-PV (solar panels) layer and the BAG “Pand” (buildings) WFS layer.
- Clipped solar points to the North Holland boundary because I don’t want some rando from Groningen in my dataset.
- Tried “Join attributes by location” to get building fields. Some stuff matched, some didn’t (QGIS can be a wild ride).

---

## 🟢 Google Maps Links & Export

- Used the Field Calculator to generate Google Maps links for every row. That part is honestly pretty satisfying.
- Exported to CSV, keeping only the fields I actually need.  
- Opened it in Excel/VSCode to check: found some blanks, especially for the special Dutch attributes.

---

## 🟢 Where My Head’s At Now

- I’m kinda torn between doing everything in code (so it’s reproducible and shareable) or just handling the last bits in QGIS.
- The network errors with Python are a pain, but at least I can show everything on GitHub.
- QGIS is good for quick checks and spatial stuff, but it’s easy to get distracted or lose track of what I was doing.

---

## 🟢 My Next Steps (To-Do List For Myself)

- [ ] Validate the current CSV for one city (maybe Haarlem) instead of trying to fix everything at once.
- [ ] See if QGIS can fill those last two fields, or if I need to do some manual work.
- [ ] Clean up/merge whatever actually works don’t start from scratch unless I have to.
- [ ] Write down every fix/step as soon as I do it so I don’t forget what worked.

---

## 🟢## Getting Just Noord-Holland Into QGIS (No More, No Less)

- [x] **Open up the PDOK Services Panel**  
  - Top menu, hit: `Plugins > PDOK Services > Open PDOK Services`

- [x] **Pick the “Bestuurlijke Gebieden” Service**  
  - In the PDOK panel’s Service dropdown, find and select:  
    `Kadaster – Bestuurlijke Gebieden`

- [x] **Choose the Province Layer**  
  - Under Layer, pick:  
    `Provinciegebied` (yup, that’s the one with all 12 Dutch provinces)

- [x] **Filter for Noord-Holland Only**  
  - Click the **Filter…** button  
  - Set this filter: `statnaam = 'Noord-Holland'`  
  - Hit **OK** (don’t skip, or you’ll get all the provinces—don’t want that)

- [x] **Add the Layer to the Map**  
  - Click **Add to Canvas** (or OK, whichever shows up)

- [x] **Check Layers Panel**  
  - Make sure a new layer called something like `Provinciegebied_noord_holland` shows up

- [x] **Find It On the Map**  
  - Zoom in or pan around until you see the Noord-Holland outline (should be a single polygon—if you see more, the filter failed)

- [x] **Rename for Sanity**  
  - Right-click the new layer in Layers panel  
  - Choose **Rename** and set it to `north_holland_boundary` (makes life easier later)

- [x] **Save My Project**  
  - Smash `Ctrl+S` or go: `Project > Save`  
  - Because nothing sucks more than doing it all again if QGIS crashes

--

## Getting Solar Data (Zon-PV) with the PDOK Plugin



## Tried Loading Zon-PV Layer – Here’s What Happened

- [x] Opened up **PDOK Services** in QGIS  
  - Went to: Plugins → PDOK Services → Open PDOK Services
- [x] Set Service to “Kadaster – Zon-PV”  
  - Looked all through the plugin for any mention of **zon-pv**
- [x] Searched “zon-pv” in the plugin  
  - Nada. Absolutely nothing came up. No solar layer to pick.
- [x] Switched to the **OGC API-Features** tab (in QGIS Data Source Manager)  
  - Tried using: `https://api.pdok.nl/kadaster/zon-pv/ogc/v1`
- [x] Hit **404 error**  
  - So, that endpoint doesn’t exist (at least, not here or not anymore).

**Conclusion:**  
- The PDOK Services plugin catalog and the OGC API endpoint both **aren’t showing Zon-PV** in my setup.
- No solar layer available by either method—so either it’s temporarily offline, I’m missing something, or PDOK just doesn’t expose it right now.

---

## Update: PDOK Zon-PV – Dead End

- Tried everything to load Zon-PV from PDOK in QGIS—no luck.
    - PDOK Services plugin: couldn’t find the zon-pv layer anywhere.
    - Tried OGC API endpoint: `https://api.pdok.nl/kadaster/zon-pv/ogc/v1` → 404 error.
    - No luck searching by name, either.

**Bottom line:**  
The Zon-PV data just isn’t showing up in the PDOK plugin or via their advertised OGC endpoint.  
Either the service is offline, the endpoint changed, or it’s just not available to me right now.

# The above one was complete failure. Figuring out other approaches.

Question is that can I use already available layers north holland boundry with new layer? 