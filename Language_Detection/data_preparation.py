#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 16 17:33:57 2020

@author: johannesheyl
"""

import utils
from config import max_word_length, language_tags
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import ModelCheckpoint, TensorBoard
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from keras.utils import np_utils
import pickle
import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


all_words_list = []
output_class = []

language_dic = {"en": 1, "de": 2, "fr": 3} 

for language in language_tags.keys():
    print("Generating data for " + language + " language!")
    x = utils.generate_dictionary(language, 20)
    all_words_list = all_words_list + x
    for i in x:
        output_class.append(language_dic[language])


vec = CountVectorizer()
vectorised_data = vec.fit_transform(all_words_list)
    
#output_class = np.asarray(output_class).reshape(-1,1)

#train_labels = to_categorical(output_class)
encoder = LabelEncoder()
encoder.fit(output_class)
encoded_Y = encoder.transform(output_class)
y = np_utils.to_categorical(encoded_Y)
x_train, x_test, y_train, y_test = train_test_split(vectorised_data, y)

def baseline_model():
    network = Sequential()
    network.add(Dense(200, input_dim=vectorised_data.shape[1], activation='sigmoid'))
    network.add(Dense(150, activation='sigmoid'))
    network.add(Dense(100, activation='sigmoid'))
    network.add(Dense(100, activation='sigmoid'))
    network.add(Dense(output_dim = y.shape[1], activation='softmax'))

    network.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    filepath = "weights.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
    return network
classifier = KerasClassifier(build_fn = baseline_model, epochs = 25, batch_size = 1024, verbose = 1)
kfold = KFold(n_splits = 2, shuffle = True)
results = cross_val_score(classifier, vectorised_data, y, cv=kfold)
print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))
classifier.fit(x_train, y_train, epochs=25, batch_size=1024, validation_data=(x_test, y_test))#, callbacks=callbacks_list)


vectorizer = joblib.load("vectoriser.pkl")
words = ["boston", "der ist", "heute", "pain", "hand"]

def predict(words):
    for i in words:
        word_list = []
        valid = False
        # while not valid:
        #     word = input('Enter word to predict:\n')
        #     if len(word) <= 20:
        #         word = word.lower()
        #         valid = True
        #     else:
        #         print('Word must be less than ' + str(20 + 1) + ' letters long')
        word = i
        
        word_list.append(word)
        vector = vec.transform(word_list)
        count = 0
        prediction_vct = classifier.predict_proba(vector)
        print(prediction_vct[0])
        langs = list(language_tags.keys())
        for i in range(len(language_tags)):
            lang = langs[i]
            score = prediction_vct[0][i]
            print(lang + ': ' + str(round(100*score, 2)) + '%')
        print('\n')

def predict(words):
    """
    

    Parameters
    ----------
    words : str
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    words = words.split(" ")
    total_classification = np.zeros(3)
    for i in words:
        word_list = []
        valid = False
        word = i
        word_list.append(word)
        vector = vec.transform(word_list)
        count = 0
        prediction_vct = classifier.predict_proba(vector)
        total_classification = total_classification + prediction_vct
        #print(prediction_vct[0])
        langs = list(language_tags.keys())
        for i in range(len(language_tags)):
            lang = langs[i]
            score = prediction_vct[0][i]
            #print(lang + ': ' + str(round(100*score, 2)) + '%')
        print('\n')
    for i in range(len(language_tags)):
        lang = langs[i]
        score = total_classification[0][i]
        print(lang + ': ' + str(round(100*score, 2)) + '%')
    return total_classification/len(words)

    


