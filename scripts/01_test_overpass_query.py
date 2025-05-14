import config, requests

# 1. build a tiny bbox around Amsterdam
bbox = (52.35, 4.88, 52.37, 4.90)

# 2. craft a minimal solar query
q = f'''
[out:json][timeout:25];
({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})
  ->.a;
way["building"](area.a)['solar'~'yes|panel'];
out count;
'''
resp = requests.post(config.OVERPASS_URL, data=q)
print("status:", resp.status_code)
print("body:", resp.text)
