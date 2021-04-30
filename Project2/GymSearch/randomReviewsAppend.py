from google.cloud import firestore
import pandas as pd
import random

def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict

def get_reviews(gym_id):
    db = firestore.Client()
    doc_ref = db.collection(u'Gyms').document(gym_id)
    # revs = []
    snapshot = doc_ref.get()
    revs = document_to_dict(snapshot)['Reviews']

    return revs

def main():
    db = firestore.Client()
    ref = db.collection(u'Gyms').stream()
    data = {}
    data = []
    for r in ref:
        print("appending ", r.id)
        revs = get_reviews(r.id)
        for t in revs:
            data.append(t)
        break
    print(type(data))
    random_revs = random.sample(data, 5)
    print("Hereeeeeeeeeeeeeeeeeeeeeeeeeeee")
    print(len(random_revs))
main()

