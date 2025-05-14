#!/usr/bin/env python3
"""
01_collect_solar_data_public_test.py

Quick smoke-test for Noord-Holland solar-building data
using the OFFICIAL Overpass + Nominatim public APIs.

Usage examples:
  # from project root
  python scripts/01_collect_solar_data_public_test.py
  # cap to 50 buildings + custom output
  python scripts/01_collect_solar_data_public_test.py --max-buildings 50 --output sample50.csv
"""

import argparse, csv, json, logging, sys, time
from pathlib import Path

import requests
import config  # must be in the same folder as this script

# CSV header; matches your field list
CSV_FIELDS = [
    "Objectnummer","Street","Housenumber","Postal code","City","Country",
    "Gebruiksdoel","Functie","Google maps link URL","Longitude LNG","Latitude LAT"
]

def build_overpass_query(area_id=None, bbox=None):
    if area_id:
        sel = f"area({area_id})"
    else:
        s,w,n,e = bbox
        sel = f"({s},{w},{n},{e})"
    solar = ['["solar"~"yes|panel"]','["roof:solar"~"yes|panel"]',
             '["generator:source"="solar"]','["building:use"="solar"]']
    filt = "".join(solar)
    return f"""
      [out:json][timeout:90];
      {sel}->.searchArea;
      (
        way["building"](area.searchArea){filt};
        relation["building"](area.searchArea){filt};
      );
      out center;
    """

def request_overpass(q):
    for i in range(1,4):
        try:
            r = requests.post(config.OVERPASS_URL, data=q.encode(), timeout=120)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logging.warning("Overpass try %d failed: %s", i, e)
            time.sleep(5*i)
    raise RuntimeError("Overpass failed after retries")

def request_nominatim(lat, lon, delay):
    params = {"format":"jsonv2","lat":f"{lat:.7f}","lon":f"{lon:.7f}","addressdetails":1}
    try:
        r = requests.get(config.NOMINATIM_URL, params=params,
                         headers={"User-Agent":"solar-test/1.0"}, timeout=30)
        r.raise_for_status()
        return r.json()
    finally:
        time.sleep(delay)

def parse_address(j):
    a = j.get("address",{})
    return {
        "Street": a.get("road",""),
        "Housenumber": a.get("house_number",""),
        "Postal code": a.get("postcode",""),
        "City": a.get("city") or a.get("town") or a.get("village") or "",
        "Country": a.get("country",""),
    }

def tags_to_purpose(tags):
    gebruik = tags.get("building:use") or tags.get("amenity") or ""
    functie = tags.get("building") or tags.get("roof:shape") or ""
    return gebruik, functie

def load_checkpoint(path):
    if not path.exists(): return []
    try: return json.loads(path.read_text("utf-8"))
    except: return []

def save_checkpoint(path, lst):
    path.write_text(json.dumps(lst), "utf-8")

def main():
    p = argparse.ArgumentParser()
    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--area-id", type=int)
    grp.add_argument("--bbox", nargs=4, type=float, metavar=("S","W","N","E"))
    p.add_argument("--max-buildings", type=int, default=25)
    p.add_argument("--output", default="sample_public.csv")
    p.add_argument("--sleep", type=float, default=1.1)
    args = p.parse_args()

    # logging
    fmt="%(asctime)s %(levelname)-7s %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt,
                        handlers=[logging.StreamHandler(sys.stdout),
                                  logging.FileHandler("solar_data_public.log","utf-8")])
    logging.info("Args: %s", args)

    area = args.area_id or (None if args.bbox else config.DEFAULT_AREA_ID)
    bbox = tuple(args.bbox) if args.bbox else (None if args.area_id else config.DEFAULT_BBOX)

    q = build_overpass_query(area, bbox)
    logging.info("Posting Overpass query…")
    data = request_overpass(q)
    elems = data.get("elements",[])
    logging.info("Overpass returned %d elements", len(elems))
    if not elems:
        logging.error("No elements – aborting.")
        sys.exit(1)

    out = Path(args.output)
    checkpoint = out.with_suffix(".checkpoint.json")
    done = load_checkpoint(checkpoint)

    with out.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        if fh.tell()==0: writer.writeheader()
        count=0
        for el in elems:
            oid = el["id"]
            if oid in done: continue
            lat = el.get("lat") or el["center"]["lat"]
            lon = el.get("lon") or el["center"]["lon"]
            try: nj = request_nominatim(lat, lon, args.sleep)
            except Exception as e:
                logging.warning("Nominatim fail %s: %s", oid, e)
                nj = {}
            addr = parse_address(nj)
            gebruik, func = tags_to_purpose(el.get("tags",{}))
            writer.writerow({
                "Objectnummer": oid,
                **addr,
                "Gebruiksdoel": gebruik,
                "Functie": func,
                "Google maps link URL": f"https://maps.google.com/?q={lat},{lon}",
                "Longitude LNG": lon,
                "Latitude LAT": lat,
            })
            done.append(oid)
            save_checkpoint(checkpoint, done)
            count+=1
            logging.info("Wrote %s (%d/%s)", oid, count,
                         "∞" if args.max_buildings==0 else args.max_buildings)
            if args.max_buildings and count>=args.max_buildings:
                break

    logging.info("Done. CSV→%s", out.resolve())

if __name__=="__main__":
    main()
