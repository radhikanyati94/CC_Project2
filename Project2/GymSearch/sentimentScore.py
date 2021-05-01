import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer 
from google.cloud import firestore
import os
cwd = os.getcwd()
nltk.data.path.append(cwd + '/nltk_data')

def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict

def sentiment_score(doc_id):
    # print("here")
    db = firestore.Client()
    query = db.collection(u'Gyms').document(doc_id)
    snapshot = query.get()
    reviews = document_to_dict(snapshot)['Reviews']
    sid = SentimentIntensityAnalyzer()
    scores = []
    # print("in here :", document_to_dict(snapshot)['Sentiment Score'])

    for r in reviews:
        # print
        text = r['review']
        ss = sid.polarity_scores(text)['compound']
        scores.append(ss)
        # print(text, ss)
        # print()
        # print()


    #print(len(reviews), len(scores))
    sentScore = sum(scores)/len(scores)
    #print(doc_id, sentScore)
    return sentScore

def list_the_gyms():
    db = firestore.Client()
    query = db.collection(u'Gyms').stream()
    docs = {}

    for doc in query:
        score = sentiment_score(doc.id)
        docs[doc.id] = score
        print(score)
        

    # sortedList = sorted(docs, key=docs.get, reverse=True)
    # return sortedList

# print(list_the_gyms())
# list_the_gyms()

