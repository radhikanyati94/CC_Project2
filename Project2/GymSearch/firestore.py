# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START bookshelf_firestore_client_import]
from google.cloud import firestore
import sentimentScore
import AddReviewType
import ExtractGymDetails
import googlemaps
from datetime import datetime
from collections import OrderedDict
import requests
import json
import reviewSummarize
import urllib.parse
# [END bookshelf_firestore_client_import]


def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict

def list_details():
    db = firestore.Client()
    query = db.collection(u'Gyms').stream()
    docs = []
    last_title = None

    for doc in query:
        docs.append(doc.id)
    return docs, last_title

def sort_list_details():
    db = firestore.Client()
    query = db.collection(u'Gyms').stream()
    gymsList = {}
    last_title = None

    for doc in query:
        query = db.collection(u'Gyms').document(doc.id)
        snapshot = query.get()
        score = document_to_dict(snapshot)['Sentiment Score']
        gymsList[doc.id] = score
    
    sortedList = sorted(gymsList, key=gymsList.get, reverse=True)
    return sortedList, last_title

def get_open_hours(doc_id):
    db = firestore.Client()
    key = 'AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok'
    # gmaps = googlemaps.Client(key='AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok')
    query = db.collection(u'Gyms').document(doc_id)
    snapshot = query.get()
    placeId = document_to_dict(snapshot)['PlaceId']
    fields = ['opening_hours']
    endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'placeid': placeId,
        'fields': ",".join(fields),
        'key': key
    }
    res = requests.get(endpoint_url, params = params)
    place_details =  json.loads(res.content)
    if len(place_details['result']) == 0:
        return "Open"
    else:
        op = place_details['result']['opening_hours']['open_now']
        if op:
            return "Open"
        else:
            return "Closed"

def list_on_pref(area):
    db = firestore.Client()
    query = db.collection(u'Gyms').stream()
    # gymsList = {}
    gymsList = OrderedDict()
    # gymsList = []
    last_title = None

    for doc in query:
        query = db.collection(u'Gyms').document(doc.id)
        snapshot = query.get()
        if document_to_dict(snapshot)['Area'] == area:            
            score = document_to_dict(snapshot)['Sentiment Score']
            gymsList[doc.id] = score
    
    sortedList = sorted(gymsList, key=gymsList.get, reverse=True)
    dict_list = []
    for l in sortedList:
        op = get_open_hours(l)
        # dict_list[l] = op
        dict_list.append((l, op))
    return dict_list, last_title, sortedList

def list_gyms_on_filter(area, filter_type, gyms_this_session):
    db = firestore.Client()
    gymsList = OrderedDict()
    last_title = None
    for doc in gyms_this_session:
        gym_ref = db.collection(u'Gyms').document(doc)
        snapshot = gym_ref.get()
        if document_to_dict(snapshot)['Area'] == area:
            events = document_to_dict(snapshot)['events']
            for e in events:
                if e['type'] == filter_type:
                    sentScore = document_to_dict(snapshot)['Sentiment Score']
                    gymsList[doc] = sentScore
                    break
    sortedList = sorted(gymsList, key=gymsList.get, reverse=True)
    dict_list = []
    for l in sortedList:
        op = get_open_hours(l)
        dict_list.append((l, op))
    return dict_list, last_title, sortedList

def list_gyms_on_filter_hours(area, filter_hour, gyms_this_session):
    gymsList = []
    last_title = None
    for g in gyms_this_session:
        if g[1] == filter_hour:
            gymsList.append((g[0], g[1]))
    return gymsList, last_title

def gyms_sorted_by_distance(user_location, gyms_list_session, city):
    last_title = None
    gymsList = []
    gmaps = googlemaps.Client(key='AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok')
    for g in gyms_list_session:
        loc = g[0] + ' ' + city
        my_dist = gmaps.distance_matrix(user_location ,loc)['rows'][0]['elements'][0]['distance']['value']
        gymsList.append((g[0], g[1], my_dist))
    gymsList.sort(key = lambda x: x[2]) 
    sortedList = [(a, b) for a, b, c in gymsList]
    return sortedList, last_title
    
def readGym(gym_id):
    db = firestore.Client()
    gym_ref = db.collection(u'Gyms').document(gym_id)
    snapshot = gym_ref.get()
    return document_to_dict(snapshot)

def readGymUser(email):
    db = firestore.Client()
    user_ref = db.collection(u'GymUsers').document(email)
    snapshot = user_ref.get()
    return document_to_dict(snapshot)

def updateGym(data, gym_id=None):
    db = firestore.Client()
    gym_ref = db.collection(u'Gyms').document(gym_id)
    gym_ref.update(data)
    return document_to_dict(gym_ref.get())

def add_review(rev, gymName):
    #print("the review is :", rev)
    db = firestore.Client()
    gym_ref = db.collection(u'Gyms').document(gymName)
    gym_ref.update({u'Reviews': firestore.ArrayUnion([rev])})
    score = sentimentScore.sentiment_score(gymName)
    # print(score)

    query_ref = db.collection(u'Gyms').document(gymName)
    gym = document_to_dict(query_ref.get())
    
    reviews = gym['Reviews']
    # print("len of reviews: ", len(reviews))
    revs = []
    
    for r in reviews: 
        revs.append(r['review'])
    
    summ, word_count =reviewSummarize.get_vectorized_matrix(revs)


    # print(word_count)
    gym_ref.update({'`Sentiment Score`': score, "Summary":summ, 'Frequent_Words' : word_count})
    # snapshot = gym_ref.get()
    # area = document_to_dict(snapshot)['Area']
    # loc = gymName + ' ' + area
    # details = ExtractGymDetails.extractDetails(loc)
    # reviews = details['Reviews']
    # revs = []
    # for r in reviews: 
    #     revs.append(r['review'])
    # summ =reviewSummarize.get_vectorized_matrix(revs)
    # word_count=reviewSummarize.wordscount(revs)
    #     # print(summ)
    # details["Frequent words"] = word_count
    # details["Summary"]=summ
    # gym_ref.update(details, merge=True)

def add_subscriber(email, gymName):
    db = firestore.Client()
    gym_ref = db.collection(u'Gyms').document(gymName)
    gym_ref.update({u'Subscribers': firestore.ArrayUnion([email])})
    return document_to_dict(gym_ref.get())

def add_gym(data):
    db = firestore.Client()
    # print(type(data["name"]))
    gymname = data["name"]
    gym_ref = db.collection(u'Gyms').document(gymname)
    del data["name"]
    gym_ref.set(data)

def add_gym_user(data):
    db = firestore.Client()
    user_ref = db.collection(u'GymUsers').document(data["email"])
    del data["email"]
    user_ref.set(data)

def add_extracted_gym_details(doc_id):
    db = firestore.Client()
    gym_ref = db.collection(u'Gyms').document(doc_id)
    snapshot = gym_ref.get()
    area = document_to_dict(snapshot)['Area']
    loc = doc_id + ' ' + area
    details = ExtractGymDetails.extractDetails(loc)
    if details is None:
        return 1
    else:
        if details["website"] != "NA" and details["website"] != "N/A" and "https://" not in details["website"] and "http://" not in details["website"]:
            details["website"] = "https://" + details["website"]
        reviews = details['Reviews']
        revs = []
        for r in reviews: 
            revs.append(r['review'])
        summ, word_count =reviewSummarize.get_vectorized_matrix(revs)
        # print(type(word_count))
        details["Frequent_Words"] = word_count
    
        # print(summ)
        details["Summary"] = summ

        gym_ref.set(details, merge=True)
        #Add type to reviews:
        AddReviewType.addType(doc_id)

        #Add sentiment score
        score = sentimentScore.sentiment_score(doc_id)
        gym_ref.set({u'Sentiment Score':score}, merge=True)
        # print("updated database")
        return 0

def getSpecificReviews(gymName,reviewType):
    db = firestore.Client()
    result = []
    docs = db.collection(u'Gyms').document(gymName).get().to_dict()
    if docs != None:
        for doc in docs:
            if doc == "Reviews":
                reviewList = docs[doc]
                for review in reviewList:
                    try:
                        if review['Type'].lower() == reviewType.lower():
                            result.append(review)
                    except Exception as inst:
                        print(inst)
                        continue
    return result

def gymLogin(email, password):
    db = firestore.Client()
    gymName = ""
    docs = db.collection(u'GymUsers').document(email).get().to_dict()
    if docs != None:
        if docs["password"] == password:
            gymName = docs["name"]
            return "Success", gymName
        else:
            return "Incorrect Password", gymName
    return "User Not Found!!", gymName


def getSubscribers(gym_id):
    db = firestore.Client()
    gym_ref = db.collection(u'Gyms').document(gym_id)
    snapshot = gym_ref.get()
    ret_list_of_subs = []
    data = document_to_dict(snapshot)
    if 'Subscribers' in data:
        subscribers = data['Subscribers']
        for s in subscribers:
            ret_list_of_subs.append(s)
    else:
        ret_list_of_subs = []
    parsed_gym_id = urllib.parse.quote(gym_id)
    parsed_url = "https://8080-cs-621499849372-default.cs-us-west1-olvl.cloudshell.dev/gyms/" + parsed_gym_id
    return ret_list_of_subs, parsed_url
    