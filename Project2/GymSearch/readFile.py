from google.cloud import firestore

db = firestore.Client()
query = db.collection(u'Gyms').stream()
docs = []
last_title = None

for doc in query:
    docs.append(doc.id)
print(docs)
