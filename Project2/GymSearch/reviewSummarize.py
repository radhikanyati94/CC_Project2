from google.cloud import firestore

import json
import csv
import pandas as pd
import numpy as np
import warnings
from sklearn.feature_extraction.text import CountVectorizer
warnings.filterwarnings("ignore")
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob
nltk.download('stopwords')
nltk.download('brown')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

stopwords = set(stopwords.words('english'))

from nltk.tokenize import word_tokenize

def extract_reviews():
    db = firestore.Client()
    query = list(db.collection(u'Gyms').stream())
    doc = query[0]
    reviews = []
    gym_ref = db.collection(u'Gyms').document(doc.id)
    snapshot = gym_ref.get().to_dict()["Reviews"]
    for s in snapshot:
        reviews.append(s['review'])

    return reviews 

def get_vectorized_matrix(t):
    print("in here")
    stopwords.add('also')
    tags = ['NN', 'PRP', 'PRP$', 'VB', 'VBD', 'WP', 'MD', 'RB', 'RBR', 'RBS']

    for txt in t:
        is_noun = lambda pos: pos[:2] in tags
        tokenized = nltk.word_tokenize(txt)
        nouns = [word for (word,pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
        example_words = nouns
        for w in example_words:
            if w not in stopwords:
                x = str(w)
                stopwords.add(x)        

    print("going to vectorize")
    cv = CountVectorizer(ngram_range=(1,1), stop_words = stopwords)
    X = cv.fit_transform(t)
    Xc = (X.T * X)
    Xc.setdiag(0)
    names = cv.get_feature_names()
    df = pd.DataFrame(data = Xc.toarray(), columns = names, index = names)

    for x in range(len(df.columns)-1,-1,-1):
        if df.columns[x].isdigit():
            df.drop(df.index[x],inplace=True)
            df.drop(df.columns[[x]],axis=1,inplace=True)
    print("deleted integer columns")
    Num_Of_Nodes = 15
    result=[]

    for x in range(len(df)):
        temp3 = [x, sum(df.iloc[x])]
        result.append(temp3)
    resultArray = np.array(result)

    a= resultArray[resultArray[:,1].argsort()[::-1]]
    for x in range(len(df)-1,-1,-1):
        if x not in a[:Num_Of_Nodes,0]:
            df.drop(df.index[x],inplace=True)
            df.drop(df.columns[[x]],axis=1,inplace=True)

    print(df)

reviews = extract_reviews()   
get_vectorized_matrix(reviews)


