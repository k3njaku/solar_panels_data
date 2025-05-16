import requests

query = "Damrak 1, Amsterdam"
url = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"
params = {
    "q": query,
    "rows": 1
}

response = requests.get(url, params=params)
data = response.json()

if data['response']['numFound'] > 0:
    doc = data['response']['docs'][0]
    print(f"Address: {doc.get('weergavenaam')}")
    print(f"Latitude: {doc.get('centroide_ll').split(' ')[1]}")
    print(f"Longitude: {doc.get('centroide_ll').split(' ')[0]}")
else:
    print("No results found.")
