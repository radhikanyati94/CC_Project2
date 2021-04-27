import googlemaps
from datetime import datetime
import requests
import json

key = 'AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok'

gmaps = googlemaps.Client(key='AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok')

loc = gmaps.geolocate()
print(loc)


URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok"
# location = input("Enter the location here: ") #taking user input
# api_key = 'YOUR_API_KEY' # Acquire from developer.here.com
# PARAMS = {'apikey':key,'q':location} 

# sending get request and saving the response as response object 

# latitude = data['items'][0]['position']['lat']
# longitude = data['items'][0]['position']['lng']

# Geocoding an address
# geocode_result = gmaps.find_place('Mountainside Fitness Tempe', 'textquery')
# print(geocode_result)                        

# placeId = geocode_result['candidates'][0]['place_id']

# fields = ['url', 'formatted_address', 'name', 'formatted_phone_number', 'opening_hours', 'website', 'rating', 'review']
# endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
# params = {
#     'placeid': placeId,
#     'fields': ",".join(fields),
#     'key': key
# }
# res = requests.get(endpoint_url, params = params)
# place_details =  json.loads(res.content)
# print(place_details['result'])
