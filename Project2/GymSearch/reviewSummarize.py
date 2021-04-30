from google.cloud import firestore

import json
import csv
import pandas as pd
import collections
import numpy as np
import warnings
from sklearn.feature_extraction.text import CountVectorizer
warnings.filterwarnings("ignore")
import nltk
import os
cwd = os.getcwd()
nltk.data.path.append(cwd + '/nltk_data')
from nltk.corpus import stopwords
from textblob import TextBlob
# nltk.download('stopwords')
# nltk.download('brown')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

stopwords = set(stopwords.words('english'))

from nltk.tokenize import word_tokenize
def get_vectorized_matrix(t):
    stopwords.add('also')
    list_of_stopwords=['*',"'",'mcclintock','site','one','two','monkey','like','rack','though','whether','able','another','every','however','next','since','tom','ty','without','last','many','sure','3rd','serious','joe','tommy','renene']
    stopwords.update(list_of_stopwords)
    tags = ['NN', 'PRP', 'PRP$', 'VB', 'VBD', 'WP', 'MD', 'RB', 'RBR', 'RBS']

    lst=[]
    for txt in t:
        is_noun = lambda pos: pos[:2] in tags
        tokenized = nltk.word_tokenize(txt)
        nouns = [word for (word,pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
        example_words = nouns
        stop_words1=set(stopwords)
    #     for im in example_words:
    #         i_split = im.split()
    #         for jm in i_split:
    #             if jm not in stop_words1:
    #                 lst.append(jm)
    # counts = collections.Counter(lst).most_common(5)

    for txt in t:
        is_noun = lambda pos: pos[:2] in tags
        tokenized = nltk.word_tokenize(txt)
        nouns = [word for (word,pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
        example_words = nouns
        for w in example_words:
            if w not in stopwords:
                x = str(w)
                stopwords.add(x)  
        for im in example_words:
            i_split = im.split()
            for jm in i_split:
                if jm not in stop_words1:
                    lst.append(jm)
    counts = collections.Counter(lst).most_common(5)

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

    Num_Of_Nodes = 10
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
    df.head().index
    df.columns

    array = df.to_numpy()
    rows,col = array.shape[0],array.shape[1]
    final_list = []
    words = list(df.columns)
    for r in range(rows):
        max_val = 0
        max_index = 0 
        for c in range(0,col): 
            if array[r][c]=="NaN":
                break 
            flag = int(array[r][c])
            if flag > max_val:
                max_val = flag 
                max_index = c          
        if max_val !=0:
            final_list.append({words[r] : words[max_index]})
            for f in final_list:
                if words[r] in f.values():
                    final_list=final_list[:-1]
    word_counts = {}
    for c in counts:
        word_counts[c[0]] = c[1]
    # print(word_counts)
    return final_list, word_counts

