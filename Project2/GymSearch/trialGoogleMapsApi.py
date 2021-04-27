import googlemaps
from datetime import datetime
import requests
import json
from google.cloud import firestore


key = 'AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok'

gmaps = googlemaps.Client(key='AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok')

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

def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict

db = firestore.Client()
query = db.collection(u'Gyms').stream()
for doc in query:
    print(doc.id)
    query = db.collection(u'Gyms').document(doc.id)
    snapshot = query.get()
    place_id = document_to_dict(snapshot)['PlaceId']
    
    fields = ['opening_hours']
    endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'placeid': place_id,
        'fields': ",".join(fields),
        'key': key
    }
    res = requests.get(endpoint_url, params = params)
    place_details =  json.loads(res.content)
    print(len(place_details))
    if len(place_details['result']) == 0:
        print("Open")
    else:
        print(place_details['result']['opening_hours']['open_now'])




