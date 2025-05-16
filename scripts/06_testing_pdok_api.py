import requests

latitude = 52.372759
longitude = 4.893604
url = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/reverse"
params = {
    "lat": latitude,
    "lon": longitude
}

response = requests.get(url, params=params)
data = response.json()

if data['response']['numFound'] > 0:
    doc = data['response']['docs'][0]
    print(f"Address: {doc.get('weergavenaam')}")
else:
    print("No address found for these coordinates.")
