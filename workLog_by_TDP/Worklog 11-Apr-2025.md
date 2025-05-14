* First run at API endpoints testing.

```python
#!/usr/bin/env python3

"""

collect_solar_data_geocoded.py

--------------------------------

Collects a sample (or full set) of buildings in Noord‑Holland (NL)

that appear to have solar panels, using ONLY the official public

Overpass + Nominatim APIs.

  

Key features

------------

• Select area via --area-id or --bbox

• Cap run size with --max-buildings (default: 25 for quick tests)

• All required columns incl. 'Gebruiksdoel' & 'Functie'

• 1‑second delay between Nominatim calls to respect the public quota

• Detailed logging to both stdout and solar_data_public.log

• Checkpoint JSON for safe resume on crash/interruption

"""

  

import argparse

import csv

import json

import logging

import sys

import time

from pathlib import Path

from typing import Dict, List, Tuple

  

import requests

  

# ---------------------------------------------------------------------------

# Public API endpoints

# ---------------------------------------------------------------------------

  

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

  

# ---------------------------------------------------------------------------

# Defaults (covering Noord‑Holland province)

# ---------------------------------------------------------------------------

  

# OSM relation 194401 -> area 3600194401

DEFAULT_AREA_ID = 3600194401

  

# south, west, north, east   (fallback if you prefer bbox mode)

DEFAULT_BBOX = (52.24, 4.55, 53.20, 5.45)

  

DEFAULT_OUTPUT = "sample_public.csv"

DEFAULT_SLEEP = 1.1            # public Nominatim: 1 request / sec

DEFAULT_MAX_BUILDINGS = 25     # small sample for smoke tests

  

# ---------------------------------------------------------------------------

# CSV header – must match the screenshot you shared

# ---------------------------------------------------------------------------

  

CSV_FIELDS = [

    "Objectnummer",

    "Street",

    "Housenumber",

    "Postal code",

    "City",

    "Country",

    "Gebruiksdoel",

    "Functie",

    "Google maps link URL",

    "Longitude LNG",

    "Latitude LAT",

]

  

# ---------------------------------------------------------------------------

# Utility helpers

# ---------------------------------------------------------------------------

  
  

def build_overpass_query(area_id: int = None,

                         bbox: Tuple[float, float, float, float] = None) -> str:

    """

    Return Overpass QL that fetches building ways/relations

    with any 'solar' hints.

    """

    if area_id:

        area_selector = f"area({area_id})"

    else:

        south, west, north, east = bbox

        area_selector = f"({south},{west},{north},{east})"

  

    solar_filters = [

        '["solar"~"yes|panel"]',

        '["roof:solar"~"yes|panel"]',

        '["generator:source"~"solar"]',

        '["building:use"="solar"]',

    ]

    filters = "".join(solar_filters)

  

    return f"""

    [out:json][timeout:90];

    {area_selector}->.searchArea;

    (

      way["building"](area.searchArea){filters};

      relation["building"](area.searchArea){filters};

    );

    out center;

    """

  
  

def request_overpass(query: str) -> Dict:

    """Fire POST to Overpass with basic retry."""

    for attempt in range(1, 4):

        try:

            resp = requests.post(OVERPASS_URL, data=query, timeout=120)

            resp.raise_for_status()

            return resp.json()

        except Exception as exc:

            logging.warning("Overpass attempt %d failed: %s", attempt, exc)

            if attempt == 3:

                raise

            time.sleep(5 * attempt)

  
  

def request_nominatim(lat: float, lon: float, delay: float) -> Dict:

    """Reverse‑geocode one coordinate pair, respecting 1 req/s public policy."""

    params = dict(format="jsonv2", lat=f"{lat:.7f}", lon=f"{lon:.7f}",

                  addressdetails=1)

    try:

        r = requests.get(NOMINATIM_URL, params=params,

                         headers={"User-Agent": "solar-test-script"}, timeout=30)

        r.raise_for_status()

        return r.json()

    finally:

        time.sleep(delay)

  
  

def parse_address(j: Dict) -> Dict[str, str]:

    """Extract address parts; blank string if missing."""

    addr = j.get("address", {})

    return dict(

        Street=addr.get("road", ""),

        Housenumber=addr.get("house_number", ""),

        **{

            "Postal code": addr.get("postcode", ""),

            "City": addr.get("city") or addr.get("town") or

                    addr.get("village") or "",

            "Country": addr.get("country", ""),

        },

    )

  
  

def tags_to_purpose(tags: Dict[str, str]) -> Tuple[str, str]:

    """Derive Gebruiksdoel / Functie from common tag keys."""

    gebruiksdoel = (tags.get("building:use") or tags.get("amenity") or

                    tags.get("shop") or tags.get("office") or "")

    functie = tags.get("building") or tags.get("roof:shape") or ""

    return gebruiksdoel, functie

  
  

def save_checkpoint(path: Path, done_ids: List[int]) -> None:

    path.write_text(json.dumps(done_ids), encoding="utf-8")

  
  

def load_checkpoint(path: Path) -> List[int]:

    if not path.exists():

        return []

    try:

        return json.loads(path.read_text(encoding="utf-8"))

    except Exception:

        return []

  
  

# ---------------------------------------------------------------------------

# Core processing

# ---------------------------------------------------------------------------

  
  

def capture_rows(elements: List[Dict],

                 out_path: Path,

                 checkpoint_path: Path,

                 max_buildings: int,

                 sleep: float):

    """

    Iterate Overpass 'elements', reverse‑geocode each centre, and

    write CSV + checkpoint as we go.

    """

    processed_ids = load_checkpoint(checkpoint_path)

    logging.info("Resuming with %d previously processed IDs", len(processed_ids))

  

    with out_path.open("a", newline="", encoding="utf-8") as fh:

        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)

        if fh.tell() == 0:

            writer.writeheader()

  

        done = 0

        for el in elements:

            osm_id = el["id"]

            if osm_id in processed_ids:

                continue

  

            lat = el.get("lat") or el["center"]["lat"]

            lon = el.get("lon") or el["center"]["lon"]

  

            try:

                nom_json = request_nominatim(lat, lon, sleep)

            except Exception as exc:

                logging.warning("Nominatim error @%s: %s", osm_id, exc)

                nom_json = {}

  

            addr = parse_address(nom_json)

            gebruiksdoel, functie = tags_to_purpose(el.get("tags", {}))

  

            writer.writerow(dict(

                Objectnummer=osm_id,

                **addr,

                **{

                    "Gebruiksdoel": gebruiksdoel,

                    "Functie": functie,

                    "Google maps link URL": f"https://maps.google.com/?q={lat},{lon}",

                    "Longitude LNG": lon,

                    "Latitude LAT": lat,

                }

            ))

  

            processed_ids.append(osm_id)

            save_checkpoint(checkpoint_path, processed_ids)

  

            done += 1

            logging.info("Wrote id=%s (%d/%d)", osm_id, done, max_buildings)

            if done >= max_buildings:

                break

  
  

def main():

    # ---------- CLI ----------------------------------------------------------

    ap = argparse.ArgumentParser(

        description="Collect solar‑building data via public OSM APIs"

    )

    grp = ap.add_mutually_exclusive_group()

    grp.add_argument("--area-id", type=int,

                     help="Overpass area id to search (default Noord‑Holland)")

    grp.add_argument("--bbox", nargs=4, type=float,

                     metavar=("SOUTH", "WEST", "NORTH", "EAST"),

                     help="Bounding box lat/lon degrees")

  

    ap.add_argument("--max-buildings", type=int, default=DEFAULT_MAX_BUILDINGS,

                    help="Limit number of buildings processed "

                         f"(default {DEFAULT_MAX_BUILDINGS})")

    ap.add_argument("--output", default=DEFAULT_OUTPUT,

                    help=f"CSV output path (default {DEFAULT_OUTPUT})")

    ap.add_argument("--sleep", type=float, default=DEFAULT_SLEEP,

                    help=f"Seconds between Nominatim calls "

                         f"(default {DEFAULT_SLEEP})")

    args = ap.parse_args()

  

    # ---------- Logging ------------------------------------------------------

    log_fmt = "%(asctime)s %(levelname)-7s %(message)s"

    logging.basicConfig(level=logging.INFO, format=log_fmt,

                        handlers=[logging.StreamHandler(sys.stdout),

                                  logging.FileHandler("solar_data_public.log",

                                                      encoding="utf-8")])

    logging.info("Args: %s", args)

  

    area_id = args.area_id or (None if args.bbox else DEFAULT_AREA_ID)

    bbox = tuple(args.bbox) if args.bbox else (None if args.area_id else DEFAULT_BBOX)

  

    # ---------- Query & process ---------------------------------------------

    query = build_overpass_query(area_id=area_id, bbox=bbox)

    logging.info("Submitting Overpass query…")

    elements = request_overpass(query).get("elements", [])

    logging.info("Overpass returned %d elements", len(elements))

  

    if not elements:

        logging.error("No elements returned – exiting.")

        sys.exit(1)

  

    out_path = Path(args.output).expanduser().resolve()

    checkpoint_path = out_path.with_suffix(".checkpoint.json")

  

    capture_rows(elements, out_path, checkpoint_path,

                 max_buildings=args.max_buildings,

                 sleep=args.sleep)

  

    logging.info("Complete! CSV saved to %s", out_path)

  
  

if __name__ == "__main__":

    main()
```

