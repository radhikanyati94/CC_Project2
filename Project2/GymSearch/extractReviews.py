from google.cloud import firestore
import pickle as pk
# Project ID is determined by the GCLOUD_PROJECT environment variable
db = firestore.Client()

def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict

document_name = "AZ Bodybuilding Personal Training Gym & Contest Prep"
#read the pickle file
data = pk.load(open("/home/ssridh55/cloudshell_open/github_radhikanyati94_cc_project2/Project2/GymSearch/AZ Bodybuilding Personal Training Gym & Contest Prep", "rb"))
# doc_ref = db.collection(u'Gyms').document(u'Mountain Fitness Tempe')


doc_ref = db.collection(u'Gyms').document(u'AZ Bodybuilding Personal Training Gym & Contest Prep')
doc_ref.set(data)
print("done, doc ref: ", doc_ref)