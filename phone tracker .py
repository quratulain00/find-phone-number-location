import os
import phonenumbers
from phonenumbers import geocoder, carrier
from opencage.geocoder import OpenCageGeocode
import folium
import sys

# API key env var se lo, warna input lo
OPENCAGE_KEY = os.environ.get("OPENCAGE_KEY")
if not OPENCAGE_KEY:
    OPENCAGE_KEY = input("Enter your OpenCage API key: ").strip()
    if not OPENCAGE_KEY:
        print("API key zaroori hai. Get one at https://opencagedata.com/")
        sys.exit(1)

number = input("Enter phone number with country code (e.g. +923001234567): ").strip()

try:
    check_number = phonenumbers.parse(number)
except Exception as e:
    print("Invalid phone number:", e)
    sys.exit(1)

number_location = geocoder.description_for_number(check_number, "en")
print("Location:", number_location)

service_provider = phonenumbers.parse(number)
print("Carrier:", carrier.name_for_number(service_provider, "en"))

geocoder_client = OpenCageGeocode(OPENCAGE_KEY)
results = geocoder_client.geocode(str(number_location))

if not results:
    print("No location found.")
    sys.exit(1)

lat = results[0]['geometry']['lat']
lng = results[0]['geometry']['lng']
print("Latitude,Longitude:", lat, lng)

map_location = folium.Map(location=[lat, lng], zoom_start=5)
folium.Marker([lat, lng], popup=number_location).add_to(map_location)
map_location.save("mylocation.html")
print("Map saved → mylocation.html")
