import tls_client
import re
import uuid
import json


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
session = tls_client.Session(
    client_identifier="chrome_130",
    random_tls_extension_order=True
)

b = input("ta ville : ")
a = input("ton addresse (rue): ")

c,d = a.replace(" ","+"), b.replace(" ","+")

getcoord = session.get(f"https://api-adresse.data.gouv.fr/search/?q={c}+{d}")
data = json.loads(getcoord.text)
coordinates = data["features"][0]["geometry"]["coordinates"]
    
longitude = coordinates[0]
latitude = coordinates[1]
print(coordinates)
print(longitude)
print(latitude)