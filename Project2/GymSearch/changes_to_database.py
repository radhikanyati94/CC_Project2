from google.cloud import firestore
import pickle as pk
import googlemaps
import nltk
from google.cloud import firestore
from nltk.sentiment.vader import SentimentIntensityAnalyzer 
import random

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')

from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import reviewSummarize


def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict

def lemmatize_sentence(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentence = []
    for word, tag in pos_tag(tokens):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
    return lemmatized_sentence

def addType(reviews):
    print("before: ", len(reviews))
    possible_words_covid = ["covid", "covid-19", "covid19", "mask", "clean", "sanitize", "distancing", "distance", "social", "social distancing", "occupancy", "safe", "dirty", "wipe","pandemic"]
    newReview = []

    for r in reviews:
        review_text = r['review']
        text_tokens = word_tokenize(review_text)
        new_list = lemmatize_sentence(text_tokens)
        f = 0
        for word in new_list:
            if word in possible_words_covid:
                f = 1
                r['Type'] = "Covid-19"
                break
        if f==0:
            r['Type'] = "General"
        print(r)
        newReview.append(r)
    print("after :", len(newReview))
    return newReview
            
def sentiment_score(reviews):
    sid = SentimentIntensityAnalyzer()
    scores = []

    for r in reviews:
        text = r['review']
        ss = sid.polarity_scores(text)['compound']
        scores.append(ss)

    sentScore = sum(scores)/len(scores)
    # print(doc_id, sentScore)
    return sentScore
# document_name = "AZ Bodybuilding Personal Training Gym & Contest Prep"
# #read the pickle file
# data = pk.load(open("/home/ssridh55/cloudshell_open/github_radhikanyati94_cc_project2/Project2/GymSearch/AZ Bodybuilding Personal Training Gym & Contest Prep", "rb"))
# # doc_ref = db.collection(u'Gyms').document(u'Mountain Fitness Tempe')


# doc_ref = db.collection(u'Gyms').document(u'AZ Bodybuilding Personal Training Gym & Contest Prep')
# doc_ref.set(data)
# print("done, doc ref: ", doc_ref)
def get_place_id(location):
    gmaps = googlemaps.Client(key='AIzaSyBOGAj_OnaB4QMmNXVQPUnSn4TXmWDDWok')

    # Geocoding an address
    geocode_result = gmaps.find_place('Mountainside Fitness Tempe', 'textquery')
    print(geocode_result)                        

    placeId = geocode_result['candidates'][0]['place_id']
    return placeId

def get_events():
    fitnessTypes = ["Yoga", "HIIT", "Zumba", "Pilates", "Kickboxing", "Full Body Fusion", "Cycling", "Personal Training"]
    daysList = ["Mon,Wed", "tue", "thurs, fri", "mon", "tue,fri", "wed, fri", "mon,wed,fri", "tue,thur,sat"]
    timesList = ["9-10am", "10-11am", "11-12pm", "4-5pm", "6-7pm"]
    occupancyList = [5, 6, 7, 4]
    events = []
    tot_events = random.randint(1, 4)
    for i in range(tot_events):
        print(i)
        event_detail = {}
        event_detail['days'] = random.choice(daysList)
        event_detail['name'] = "abc"
        event_detail['occupancy'] = random.choice(occupancyList)
        event_detail['time'] = random.choice(timesList)
        event_detail['type'] = random.choice(fitnessTypes)

        events.append(event_detail)
    return events

def add_gym_and_details(data, name):
    db = firestore.Client()
    doc_ref = db.collection(u'Gyms').document(name)
    loc = name + ' ' + "Tempe"
    place_id = get_place_id(loc)
    sentScore = sentiment_score(data['Reviews'])
    reviews_with_type = addType(data['Reviews'])
    sessions = get_events()
    
    covid_guidelines = "Equipment must be wiped before and after use with sanitising wipes. Temperature will be checked for every person entering the Gym. Everyone should stand only on the marked areas of the floor while waiting for equipment. All the halls and group classes should be booked in advance. Walk in is not allowed. Consumption of food is not allowed inside the Gym. Everyone should wear a mask at all times. Showers are closed temporarily. Cafe and Spa are closed to minimise the spread of Covid-19. Use of scarves, ski masks and balaclavas are not allowed as substitute for masks. Cash registers and information desk are closed temporarily and unnecessary interaction is not encouraged. Resistance bands, yoga mats, yoga blocks, foam roller, other personal items must not be shared with others."

    #get sentiment score


    to_add={}
    to_add['Area'] = "Tempe"
    to_add['PlaceId'] = place_id
    to_add['Reviews'] = reviews_with_type
    to_add['Sentiment Score'] = sentScore
    to_add['Time'] = data['Time']
    to_add['events'] = sessions
    to_add['location'] = data['location']
    to_add['occupancy'] = "20"
    to_add['rating'] = data['rating']
    to_add['website'] = data['website']
    to_add['covidGuidelines'] = covid_guidelines

    doc_ref.set(to_add)
    print(to_add)


name = "Planet Fitness"
data = pk.load(open("/home/ssridh55/cloudshell_open/github_radhikanyati94_cc_project2/Project2/GymSearch/Planet Fitness", "rb"))

add_gym_and_details(data, name)





# db = firestore.Client()
# query = db.collection(u'Gyms').stream()
# docs = {}
# for doc in query:
#     if doc.id == "Spot Fitness and Spa":
#         gym_ref = db.collection(u'Gyms').document(doc.id)
#         snapshot = gym_ref.get()
#         sentScore = document_to_dict(snapshot)['Sentiment Score']
#         gym_ref.update({'`Sentiment Score`' : 1})
#         print(sentScore)

