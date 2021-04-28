import googlemaps
from datetime import datetime
import requests
import json
from google.cloud import firestore
import random


# key = 'AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok'

# gmaps = googlemaps.Client(key='AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok')

# # Geocoding an address
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
# # print(place_details['result'])
# # print(place_details['result']['opening_hours']['weekday_text'])

# revs = []
# reviewsObtained = place_details['result']['reviews']
# for r in reviewsObtained:
#     reviewforthis = {}
#     reviewforthis['date'] = r['relative_time_description']
#     reviewforthis['name'] = r['author_name']
#     reviewforthis['rating'] = str(r['rating']) + ' stars'
#     reviewforthis['review'] = r['text']
#     revs.append(reviewforthis)

# print(revs)

def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict

fitnessType = "Kickboxing"
area = "Tempe"
db = firestore.Client()
query = db.collection(u'Gyms').stream()
gyms = {}
for doc in query:
    gym_ref = db.collection(u'Gyms').document(doc.id)
    snapshot = gym_ref.get()
    if document_to_dict(snapshot)['Area'] == area:
        events = document_to_dict(snapshot)['events']
        for e in events:
            if e['type'] == fitnessType:
                sentScore = document_to_dict(snapshot)['Sentiment Score']
                gyms[doc.id] = sentScore
                break
sortedList = sorted(gyms, key=gyms.get, reverse=True)
print(sortedList)

# fitnessTypes = ["Yoga", "HIIT", "Zumba", "Pilates", "Kickboxing", "Full Body Fusion", "Cycling", "Personal Training"]
# daysList = ["Mon,Wed", "tue", "thurs, fri", "mon", "tue,fri", "wed, fri", "mon,wed,fri", "tue,thur,sat"]
# timesList = ["9-10am", "10-11am", "11-12pm", "4-5pm", "6-7pm"]
# occupancyList = [5, 6, 7, 4]

# db = firestore.Client()
# query = db.collection(u'Gyms').stream()
# for doc in query:
#     events = []
#     gym_ref = db.collection(u'Gyms').document(doc.id)
#     tot_events = random.randint(1, 4)
#     for i in range(tot_events):
#         event_detail = {}
#         event_detail['days'] = random.choice(daysList)
#         event_detail['name'] = "abc"
#         event_detail['occupancy'] = random.choice(occupancyList)
#         event_detail['time'] = random.choice(timesList)
#         event_detail['type'] = random.choice(fitnessTypes)

#         events.append(event_detail)
    
#     gym_ref.set({u'events':events}, merge=True)
#     print("done for ", doc.id)



    











# db = firestore.Client()
# query = db.collection(u'Gyms').stream()
# for doc in query:
#     print(doc.id)
#     query = db.collection(u'Gyms').document(doc.id)
#     snapshot = query.get()
#     place_id = document_to_dict(snapshot)['PlaceId']
    
#     fields = ['opening_hours']
#     endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
#     params = {
#         'placeid': place_id,
#         'fields': ",".join(fields),
#         'key': key
#     }
#     res = requests.get(endpoint_url, params = params)
#     place_details =  json.loads(res.content)
#     print(len(place_details))
#     if len(place_details['result']) == 0:
#         print("Open")
#     else:
#         print(place_details['result']['opening_hours']['open_now'])




