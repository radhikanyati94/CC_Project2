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
import requests
import json
# [END bookshelf_firestore_client_import]


def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict


# def next_page(limit=10, start_after=None):
#     db = firestore.Client()

#     query = db.collection(u'Book').limit(limit).order_by(u'title')

#     if start_after:
#         # Construct a new query starting at this document.
#         query = query.start_after({u'title': start_after})

#     docs = query.stream()
#     docs = list(map(document_to_dict, docs))

#     last_title = None
#     if limit == len(docs):
#         # Get the last document from the results and set as the last title.
#         last_title = docs[-1][u'title']
#     return docs, last_title

def list_details():
    db = firestore.Client()
    query = db.collection(u'Gyms').stream()
    docs = []
    last_title = None

    for doc in query:
        docs.append(doc.id)
    #print(docs)
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
            return "Open Now!"
        else:
            return "Closed"

def list_on_pref(area):
    db = firestore.Client()
    query = db.collection(u'Gyms').stream()
    gymsList = {}
    last_title = None

    for doc in query:
        query = db.collection(u'Gyms').document(doc.id)
        snapshot = query.get()
        # print(document_to_dict(snapshot))
        if document_to_dict(snapshot)['Area'] == area:            
            score = document_to_dict(snapshot)['Sentiment Score']
            gymsList[doc.id] = score
    
    sortedList = sorted(gymsList, key=gymsList.get, reverse=True)
    # print(gymsList)
    dict_list = {}
    for l in sortedList:
        op = get_open_hours(l)
        dict_list[l] = op
    return dict_list, last_title

# @app.route('/gyms/<gym_id>')
def viewGym(gym_id):
    gym = firestore.readGym(gym_id)
    review_summary=reviewSummarize.get_vectorized_matrix(reviewSummarize.extract_reviews())
    return render_template('view_gym.html', gym=gym, gym_id=gym_id)
    # , review_summary=review_summary)


def read(book_id):
    # [START bookshelf_firestore_client]
    db = firestore.Client()
    book_ref = db.collection(u'Book').document(book_id)
    snapshot = book_ref.get()
    # [END bookshelf_firestore_client]
    return document_to_dict(snapshot)
    
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

def update(data, book_id=None):
    db = firestore.Client()
    book_ref = db.collection(u'Book').document(book_id)
    book_ref.set(data)
    return document_to_dict(book_ref.get())

create = update

def add_review(rev, gymName):
    #print("the review is :", rev)
    db = firestore.Client()
    gym_ref = db.collection(u'Gyms').document(gymName)
    gym_ref.update({u'Reviews': firestore.ArrayUnion([rev])})

    #Add sentiment score
    score = sentimentScore.sentiment_score(gymName)
    print(score)
    gym_ref.update({'SentimentScore': score})

def add_gym(data):
    db = firestore.Client()
    gym_ref = db.collection(u'Gyms').document(data["name"])
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

    gym_ref.set({details}, merge=True)

    #Add type to reviews:
    AddReviewType.addType(doc_id)

def delete(id):
    db = firestore.Client()
    book_ref = db.collection(u'Book').document(id)
    book_ref.delete()

def getSpecificReviews(gymName,reviewType):
    db = firestore.Client()
    result = []
    docs = db.collection(u'Gyms').document(gymName).get().to_dict()
    for doc in docs:
        if doc == "Reviews":
            reviewList = docs[doc]
            for review in reviewList:
                try:
                    if review['type'].lower() == reviewType.lower():
                        result.append(review)
                except Exception as inst:
                    print(inst)
                    continue
    return result

        
#getSpecificReviews("Equipments", "Lakeside Fitness")