#!/usr/bin/env python3
"""
01_test_overpass_query.py
— verify that Overpass returns some solar-tagged buildings
and log the full response to a file.
"""

import logging
import config
import requests

# 1. set up logging to both stdout and test_overpass.log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s",
    handlers=[
        logging.StreamHandler(),  # console
        logging.FileHandler("test_overpass.log", mode="w", encoding="utf-8")
    ]
)

# 2. define a small bbox around central Amsterdam
south, west, north, east = 52.35, 4.88, 52.37, 4.90

# 3. build an Overpass count query for solar-tagged buildings
query = f"""
[out:json][timeout:25];
way["building"]({south},{west},{north},{east})['solar'~'yes|panel'];
out count;
"""

logging.info("Posting query to %s", config.OVERPASS_URL)
resp = requests.post(config.OVERPASS_URL, data=query)
logging.info("HTTP status: %d", resp.status_code)
logging.info("Response body:\n%s", resp.text)
