#!/usr/bin/env python3
"""
collect_solar_data_public_test.py

Pulls a *sample* of buildings with solar‑panel tags in Noord‑Holland
using the OFFICIAL Overpass + Nominatim public APIs.

Designed for quick validation before switching to a self‑hosted stack.
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import requests

# ------------- Default endpoints ------------------------------------------------

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

# ------------- Default query scope ---------------------------------------------
# Overpass *area* relation ID for the Dutch province Noord‑Holland
# (relation 194401 in OSM => area ID 3600194401)
DEFAULT_AREA_ID = 3600194401

# A fallback bounding box that roughly covers Noord‑Holland
# south, west, north, east
DEFAULT_BBOX = (52.24, 4.55, 53.20, 5.45)

# ------------- CSV header ------------------------------------------------------

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

# ------------- Helper functions -------------------------------------------------


def build_overpass_query(area_id: int = None, bbox: Tuple[float, float, float, float] = None) -> str:
    """
    Create an Overpass QL query that fetches building *ways* or *relations*
    tagged with anything that hints at solar panels.

    If *area_id* is given, we search inside that area.
    Otherwise a bounding box must be provided.
    """
    area_selector = f"area({area_id})" if area_id else f"({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})"

    # Many datasets tag solar installations differently; we cast a wide net:
    solar_filters = [
        '["solar"~"yes|panel"]',
        '["roof:solar"~"yes|panel"]',
        '["generator:source"~"solar"]',
        '["building:use"="solar"]',
    ]
    filter_str = "".join(solar_filters)

    query = f"""
    [out:json][timeout:90];
    {area_selector}->.searchArea;
    (
      way["building"](area.searchArea){filter_str};
      relation["building"](area.searchArea){filter_str};
    );
    out center {{}};
    """
    return query


def call_overpass(query: str) -> Dict:
    """POST the query to Overpass and return parsed JSON, with basic retry logic."""
    tries = 3
    for attempt in range(1, tries + 1):
        try:
            r = requests.post(OVERPASS_URL, data=query.encode("utf-8"), timeout=120)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            logging.warning("Overpass attempt %s/%s failed: %s", attempt, tries, exc)
            if attempt == tries:
                raise
            time.sleep(5 * attempt)


def reverse_geocode(lat: float, lon: float, sleep: float = 1.1) -> Dict:
    """
    Hit public Nominatim for one coordinate pair.
    Respects the 1 request / second usage policy by sleeping after each call.
    """
    params = {
        "format": "jsonv2",
        "lat": f"{lat:.7f}",
        "lon": f"{lon:.7f}",
        "addressdetails": 1,
    }
    try:
        res = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": "solar-test/0.1"}, timeout=30)
        res.raise_for_status()
        return res.json()
    finally:
        time.sleep(sleep)  # good citizenship


def parse_address(nominatim_json: Dict) -> Dict[str, str]:
    """
    Pull out street / housenumber / postcode / city / country from a Nominatim reply.
    Some fields may be missing; default to empty string.
    """
    addr = nominatim_json.get("address", {})
    return {
        "Street": addr.get("road", ""),
        "Housenumber": addr.get("house_number", ""),
        "Postal code": addr.get("postcode", ""),
        "City": addr.get("city") or addr.get("town") or addr.get("village") or "",
        "Country": addr.get("country", ""),
    }


def osm_tags_to_purpose(tags: Dict[str, str]) -> Tuple[str, str]:
    """
    Convert raw OSM tags into our Gebruiksdoel (use) and Functie (function) strings.
    Very heuristic.
    """
    gebruiksdoel = tags.get("building:use") or tags.get("amenity") or tags.get("shop") or tags.get("office") or ""
    functie = tags.get("building") or tags.get("roof:shape") or ""
    return gebruiksdoel, functie


def checkpoint_save(path: Path, done_ids: List[int]) -> None:
    """Dump processed OSM IDs so we can resume."""
    with path.open("w", encoding="utf-8") as fh:
        json.dump(done_ids, fh)


def checkpoint_load(path: Path) -> List[int]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


# ------------- Main processing --------------------------------------------------


def process_elements(elements: List[Dict], max_buildings: int, out_csv: Path, checkpoint: Path, sleep: float):
    done_ids = checkpoint_load(checkpoint)
    logging.info("Loaded %d processed IDs from checkpoint", len(done_ids))

    with out_csv.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        if fh.tell() == 0:  # new file – write header
            writer.writeheader()

        processed = 0
        for el in elements:
            osm_id = el["id"]
            if osm_id in done_ids:
                continue

            lat, lon = el.get("lat") or el["center"]["lat"], el.get("lon") or el["center"]["lon"]

            # reverse‑geocode
            try:
                nom_res = reverse_geocode(lat, lon, sleep=sleep)
            except Exception as exc:
                logging.warning("Reverse geocode failed for %s: %s", osm_id, exc)
                nom_res = {}

            addr_map = parse_address(nom_res)
            gebruiksdoel, functie = osm_tags_to_purpose(el.get("tags", {}))

            row = {
                "Objectnummer": osm_id,
                **addr_map,
                "Gebruiksdoel": gebruiksdoel,
                "Functie": functie,
                "Google maps link URL": f"https://maps.google.com/?q={lat},{lon}",
                "Longitude LNG": lon,
                "Latitude LAT": lat,
            }

            writer.writerow(row)
            done_ids.append(osm_id)
            processed += 1
            checkpoint_save(checkpoint, done_ids)

            logging.info("Captured id=%s (%d/%d)", osm_id, processed, max_buildings)

            if processed >= max_buildings:
                break


def main():
    parser = argparse.ArgumentParser(
        description="Collect a sample of North‑Holland solar‑building data via public APIs"
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--area-id", type=int, help="Overpass 'area' id to search inside")
    g.add_argument(
        "--bbox",
        nargs=4,
        type=float,
        metavar=("SOUTH", "WEST", "NORTH", "EAST"),
        help="Bounding box to search inside (lat/lon degrees)",
    )
    parser.add_argument("--max-buildings", type=int, default=25, help="Cap number of buildings processed")
    parser.add_argument("--output", default="sample_public.csv", help="CSV output file")
    parser.add_argument("--sleep", type=float, default=1.1, help="Seconds to sleep between Nominatim calls")
    args = parser.parse_args()

    # -------------------------------------------------------------------------
    log_fmt = "%(asctime)s  %(levelname)-8s %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt, handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("solar_data_test.log", encoding="utf-8")
    ])
    logging.info("Start run with args: %s", args)

    area_id = args.area_id or (None if args.bbox else DEFAULT_AREA_ID)
    bbox = tuple(args.bbox) if args.bbox else (None if args.area_id else DEFAULT_BBOX)

    query = build_overpass_query(area_id=area_id, bbox=bbox)
    logging.info("Posting Overpass query…")
    overpass_json = call_overpass(query)
    elements = overpass_json.get("elements", [])
    logging.info("Overpass returned %d elements", len(elements))

    if not elements:
        logging.error("Nothing returned – exiting.")
        sys.exit(1)

    out_csv = Path(args.output)
    checkpoint = out_csv.with_suffix(".checkpoint.json")

    process_elements(
        elements=elements,
        max_buildings=args.max_buildings,
        out_csv=out_csv,
        checkpoint=checkpoint,
        sleep=args.sleep,
    )

    logging.info("Done! CSV saved to %s", out_csv.resolve())


if __name__ == "__main__":
    main()
