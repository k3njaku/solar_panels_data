#!/usr/bin/env python3
"""
inspect_overpass_structure.py

Fetches a small sample of building ways in Noord-Holland
(without any solar filter) and pretty-prints their JSON keys
so you can see exactly which tags are present.
"""

import json
import logging
import requests
import config  # must be in the same folder

# — configure simple console logging —
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s"
)

# — build an Overpass query with no solar filter —
# here using the default area ID for Noord-Holland
query = f"""
[out:json][timeout:25];
area({config.DEFAULT_AREA_ID})->.a;
way["building"](area.a);
out center 5;  # get only 5 elements for quick inspection
"""

logging.info("Querying Overpass for 5 building elements in Noord-Holland")
resp = requests.post(config.OVERPASS_URL, data=query)
resp.raise_for_status()
data = resp.json().get("elements", [])

# — inspect each element’s structure —
for i, el in enumerate(data, start=1):
    logging.info("Element #%d: OSM id=%s, type=%s", i, el.get("id"), el.get("type"))
    # print top-level keys
    print("  top-level keys:", list(el.keys()))
    # if there’s a tags dict, print its keys
    tags = el.get("tags", {})
    if tags:
        print("  tags keys    :", list(tags.keys()))
    print("-" * 60)

