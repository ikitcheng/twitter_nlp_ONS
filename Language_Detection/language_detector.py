#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 16 17:33:57 2020

@author: johannesheyl
"""

import utils
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from keras.utils import np_utils
import joblib
from sklearn.feature_extraction.text import CountVectorizer
import wikipedia as wiki
import unidecode
import re
from tensorflow.keras.callbacks import ModelCheckpoint

class Language_Detector:
    def __init__(self, languages):
        """
        

        Parameters
        ----------
        languages : list
            A list of languages that the neural network will be trained on. 
            Each language needs to be one that is available on Wikipedia, using
            the (typically two-letter) codes.

        """
        self.languages = languages
        
        self.lang_dict = {}
        
        for i, lang in enumerate(languages):
            self.lang_dict[lang] = i
            
    def clean(self, page_content):
        words = re.sub(r'[^a-zA-Z ]', '', page_content)
        lower = words.lower()
        word_list = lower.split()
        return word_list
     
            
    def generate_dictionary_for_each_language(self, number_of_words_per_lang = 50000):
        """
        

        Parameters
        ----------
        number_of_words_per_lang : int, optional
            The minimum number of words from each language that
            should be included during training.

        Returns
        -------
        lst : list
            A list of all the words of each language.
        output_class : list
            A list of the language labels for each word in "lst"

        """
        self.all_words_list = []
        self.output_class = []
        for language in self.languages:
            wiki.set_lang(language)
            
            lst = []
            
            #while len(list_of_acceptable_topics) < 100:
            while len(list(set(lst)))< number_of_words_per_lang:
                try:
                    topic = wiki.random()
                    page = wiki.page(topic)
                    content = page.content
                    content = unidecode(content)
                    lst = lst + self.clean(content)
                except wiki.DisambiguationError: # skip if there is more than one Wikipedia page with that topic
                    pass
                except wiki.PageError: # skip if page can't be accessed for some reason
                    pass
            self.all_words_list = self.all_words_list + lst
            for i in lst:
                self.output_class.append(self.lang_dict[language])

        return self.all_words_list, self.output_class
    
    def vectorise(self):
        self.vec = CountVectorizer()
        self.vectorised_data = self.vec.fit_transform(self.all_words_list)
            
        encoder = LabelEncoder()
        encoder.fit(self.output_class)
        encoded_Y = encoder.transform(self.output_class)
        self.y = np_utils.to_categorical(encoded_Y)
        
        
    def train(self):
        def baseline_model():
            network = Sequential()
            network.add(Dense(200, input_dim=self.vectorised_data.shape[1], activation='sigmoid'))
            network.add(Dense(150, activation='sigmoid'))
            network.add(Dense(100, activation='sigmoid'))
            network.add(Dense(100, activation='sigmoid'))
            network.add(Dense(output_dim = self.y.shape[1], activation='softmax'))
        
            network.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
            filepath = "weights.hdf5"
            checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
            return network
        
        x_train, x_test, y_train, y_test = train_test_split(self.vectorised_data, self.y)
        
    
        self.classifier = KerasClassifier(build_fn = baseline_model, epochs = 25, batch_size = 1024, verbose = 1)
        kfold = KFold(n_splits = 2, shuffle = True)
        results = cross_val_score(self.classifier, self.vectorised_data, self.y, cv=kfold)
        print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))
        self.classifier.fit(x_train, y_train, epochs=25, batch_size=1024, validation_data=(x_test, y_test))#, callbacks=callbacks_list)

    def predict(self, words):
        """
        
        Parameters
        ----------
        words : str
            String of text where each word is separated by a space.
    
        Returns
        -------
        output: array 
            An array consisting of the probability that the input is of each language
    
        """
        
        words = words.split(" ")
        total_classification = np.zeros(len(self.languages))
        for i in words:
            word_list = []
            word_list.append(i)
            vector = self.vec.transform(word_list)
            prediction_vct = self.classifier.predict_proba(vector)
            total_classification = total_classification + prediction_vct
            langs = list(self.lang_dict.keys())
            for i in range(len(langs)): # gives the breakdown for each language
                lang = langs[i]
                score = prediction_vct[0][i]
            print('\n')
        for i in range(len(langs)):
            lang = langs[i]
            score = total_classification[0][i]
            print(lang + ': ' + str(round(100*score, 2)) + '%')
        output = total_classification/len(words)
        return output

        




