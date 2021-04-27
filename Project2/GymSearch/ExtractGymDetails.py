import googlemaps
from datetime import datetime
import requests
import json

def extractDetails(location):

    key = "AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok"
    #This function extracts the google map details of a gym, once it is registered to this application.
    gmaps = googlemaps.Client(key='AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok')

    # Geocoding an address
    geocode_result = gmaps.find_place(location, 'textquery')
    print(geocode_result)                        

    placeId = geocode_result['candidates'][0]['place_id']

    fields = ['url', 'formatted_address', 'name', 'formatted_phone_number', 'opening_hours', 'website', 'rating']#, 'review']
    endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'placeid': placeId,
        'fields': ",".join(fields),
        'key': key
    }
    res = requests.get(endpoint_url, params = params)
    place_details =  json.loads(res.content)
    print(place_details['result'])

    result = {}
    result['location'] = place_details['result']['formatted_address']
    result['rating'] = place_details['result']['rating']
    result['website'] = place_details['result']['website']
    result['place_id'] = placeId
    result['Reviews'] = place_details['result']['review']
    result['Time'] = place_details['result']['weekday_text']
    return result

# extractDetails("Mountainside Fitness Tempe/Marina Heights, 300 E Rio Salado Pkwy #102, Tempe, AZ 85281, USA")

