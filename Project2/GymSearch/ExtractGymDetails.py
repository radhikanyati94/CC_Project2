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
    # print(geocode_result)                        
    if len(geocode_result['candidates']) == 0:
        return None

    placeId = geocode_result['candidates'][0]['place_id']

    fields = ['url', 'formatted_address', 'name', 'formatted_phone_number', 'opening_hours', 'website', 'rating', 'review']
    endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'placeid': placeId,
        'fields': ",".join(fields),
        'key': key
    }
    res = requests.get(endpoint_url, params = params)
    place_details =  json.loads(res.content)
    # print(place_details['result'])
    revs = []
    reviewsObtained = place_details['result']['reviews']
    for r in reviewsObtained:
        reviewforthis = {}
        reviewforthis['date'] = r['relative_time_description']
        reviewforthis['name'] = r['author_name']
        reviewforthis['rating'] = str(r['rating']) + ' stars'
        reviewforthis['review'] = r['text']
        revs.append(reviewforthis)
    result = {}
    # result['location'] = place_details['result']['formatted_address']
    result['rating'] = place_details['result']['rating']
    result['website'] = place_details['result']['website']
    result['PlaceId'] = placeId
    result['Reviews'] = revs
    result['Time'] = place_details['result']['opening_hours']['weekday_text']
    return result

# extractDetails("Mountainside Fitness Tempe/Marina Heights, 300 E Rio Salado Pkwy #102, Tempe, AZ 85281, USA")

