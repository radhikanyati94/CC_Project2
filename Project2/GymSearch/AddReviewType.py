import nltk
from google.cloud import firestore
from nltk.sentiment.vader import SentimentIntensityAnalyzer 

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')

import os
cwd = os.getcwd()
nltk.data.path.append(cwd + '/nltk_data')

from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize

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

def addType(doc_id):
    db = firestore.Client()
    query = db.collection(u'Gyms').document(doc_id)
    snapshot = query.get()
    reviews = document_to_dict(snapshot)['Reviews']
    print("before: ", len(reviews))
    possible_words_covid = ["covid", "covid-19", "covid19", "mask", "clean", "sanitize", "distancing", "distance", "social", "social distancing", "occupancy", "safe", "dirty", "wipe","pandemic"]
    newReview = []

    for r in reviews:
        # print(r)
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
    # print(new_list)
    print("after :", len(newReview))
    query.set({u'Reviews':newReview}, merge=True)
            
def sentiment_score(doc_id):
    print("here")
    db = firestore.Client()
    query = db.collection(u'Gyms').document(doc_id)
    snapshot = query.get()
    reviews = document_to_dict(snapshot)['Reviews']
    sid = SentimentIntensityAnalyzer()
    scores = []

    for r in reviews:
        text = r['review']
        ss = sid.polarity_scores(text)['compound']
        scores.append(ss)
        # print(text, ss)
        # print()
        # print()
    # print(len(reviews), len(scores))
    sentScore = sum(scores)/len(scores)
    # print(doc_id, sentScore)
    query.set({u'Sentiment Score':sentScore}, merge=True)
    return sentScore

def read_the_gyms():
    db = firestore.Client()
    query = db.collection(u'Gyms').stream()

    for doc in query:
        print("executing ", doc.id)
        addType(doc.id)
        score = sentiment_score(doc.id)
        print(doc.id, score)

    print("Done")
    


def main():
    #This function is for trial
    db = firestore.Client()
    frank_ref = db.collection(u'Book').document(u'frank')
    frank_ref.set({
        u'name': u'Frank',
        u'age': 12
    })

    rev = { u'food': u'Pizza',
            u'color': u'Blue',
            u'subject': u'Recess'}

    rev2 = { u'food': u'Pizza',
            u'color': u'Blue',
            u'subject': u'math'}
    frank_ref.update({u'Reviews': firestore.ArrayUnion([rev])})
    frank_ref.update({u'Reviews': firestore.ArrayUnion([rev2])})

    snapshot = frank_ref.get()
    reviews = document_to_dict(snapshot)['Reviews']
    newField = []
    for r in reviews:
        r['type'] = "sam"
        newField.append(r)
    frank_ref.set({u'Reviews':newField}, merge=True)
    frank_ref.set({u'Sentiment Score':1}, merge=True)
    
    print("done")

# read_the_gyms()
# main()