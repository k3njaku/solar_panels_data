# scripts/config.py

# Official public endpoints
OVERPASS_URL   = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL  = "https://nominatim.openstreetmap.org/reverse"

# OSM relation 194401 -> area 3600194401 (Noord-Holland province)
DEFAULT_AREA_ID = 3600194401

# Fallback bbox: south, west, north, east
DEFAULT_BBOX    = (52.24, 4.55, 53.20, 5.45)
