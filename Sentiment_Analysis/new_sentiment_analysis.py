#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 21 16:02:17 2020

@author: johannesheyl
"""

import numpy as np
import pandas as pd
import ast
import os
import re
from nltk.tokenize import TweetTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
import joblib
import matplotlib.pyplot as plt




#filename = "/Users/johannesheyl/Downloads/drive-download-20200511T142854Z-001/scrape_data_2020-05-03-2020-05-04/en_billgatesisnotadoctor.csv"
filename = "/Users/johannesheyl/Dropbox/PhD/Group_Project/Covid-19_sentiment_analysis/test_csv_file"
tweet_column_name = "text"
headers_master =  ["created_at", "id", "text", "entities", "source", 
            "user", "user.id", "username", "user.location", 
            "user.followers_count", "user.friends_count", "user.created_at",
            "user.favourites_count", "user.statuses_count", "user.verified",
            "user.statuses_count2", "geo", "coordinates", "place", "retweeted_status.text", 
            "retweet_count", "tweet_favorite_count", "tweet_retweeted", "tweet_favorited"]


pro_lockdown_hashtags = ["covidiot45", "socialdistancing", "stayathome",
                         "istayathome", "StayHomeStaySafe", "stayhomesavelives",
                         "stayhome", "quarantineandchill", "covidiots", "mypandemicsurvivalplan",
                         "flattenthecurve", "togetherathome", "bigonlinepar", "extendlockdown"]

anti_lockdown_hashtags = ["americaworkstogether", "firefauci", "ReopenAmericanNow",
                          "StopTheMadness", "operationgridlock", "saynotobillgates",
                          "saynotovaccines", "vaccineskill", "billgatesisnotadoctor",
                          "billgatesisnotourfriend", "billgatesbioterrorist", 
                          "covidhoax", "endthelockdownnow", "vaccinesarenottheanswer",
                          "endthelockdownuk"]

list_of_hashtag_lists = [pro_lockdown_hashtags, anti_lockdown_hashtags]
list_of_classes = [1,-1]

class new_sentiment_analyser:
    def __init__(self, filename, tweet_column_name, headers = None, list_of_classes = list_of_classes, classification_col_name = None):
        self.filename = filename
        self.tweet_column_name = tweet_column_name
        self.headers = headers
        self.list_of_classes = list_of_classes
        self.classification_col_name = classification_col_name
        
        if headers is None:
            self.headers = headers_master
            
        self.df = pd.read_csv(filename, 
             encoding = "ISO-8859-1", header = None, names = self.headers)

        if "Hashtags" not in self.headers:
            self.find_hashtags()
            
        if self.classification_col_name is None:
            self.hashtag_classification_labeler(list_of_hashtag_lists, list_of_classes)
            
    def find_hashtags(self, hashtag_content_col = "entities"):
        
        tweet_col = self.df[hashtag_content_col].values
        list_of_hashtags = []
        
        for i, tweet_info in enumerate(tweet_col[1]):
            hashtags_for_that_row = []
            for dic in ast.literal_eval(tweet_info)["hashtags"]:
                hashtags_for_that_row.append(dic["text"].lower())
            list_of_hashtags.append(hashtags_for_that_row)
        
        self.df["Hashtags"] = list_of_hashtags
        
    
    def hashtag_classification_labeler(self, list_of_hashtag_lists, list_of_classes):
        """
        
        Parameters
        ----------
        list_of_hashtag_lists : array
            An array in which each subarray contains the hashtags associated with
            a particular class (for example, the first subarray contains the hashtags
            associated with positive sentiment tweets, the second with negative sentiment tweets, etc)
        list_of_classes : array
            An array of the same length as list_of_hashtag_lists. Each element 
            is a class label.

        Returns
        -------
        None.

        """
        labels = []
        for i, hashtags in enumerate(self.df.Hashtags.values):
            temp_label = None
            for j, liste in enumerate(list_of_hashtag_lists):
                if bool(set(self.df.Hashtags.values[0]) & set(liste)):
                    temp_label = list_of_classes[j]
                    labels.append(list_of_classes[j])
                    break
            if temp_label == None:
                labels.append(None)
                    
        self.df["Labels"] = labels
        #print(len(labels))
        #print(len(self.df.Hashtags.values))
        
    def clean_tweets(self):
        self.eliminate_url_from_tweets()
        self.eliminate_twitter_handles()
        self.eliminate_hashtags()
        
    def eliminate_url_from_tweets(self):
        for i, tweet in enumerate(self.df[self.tweet_column_name].values):
            self.df[self.tweet_column_name].values[i] =  re.sub(r'http\S+', '', tweet)

    def eliminate_twitter_handles(self):
        tokenizer = TweetTokenizer(strip_handles = True)
        for i, tweet in enumerate(self.df[tweet_column_name].values):
            tokenized_tweet = tokenizer.tokenize(tweet)
            self.df[self.tweet_column_name].values[i] = ' '.join(tokenized_tweet)

    def eliminate_hashtags(self):
        for i, tweet in enumerate(self.df[tweet_column_name].values):
            self.df[tweet_column_name].values[i] =  re.sub(r'#\S+', '', tweet)

    
    def preprocess_data(self, vectorizer = "count", number_of_features = 10000, ngram_range = (1,1)):
        if vectorizer == "count":
            self.vectorizer = CountVectorizer(max_features=number_of_features, min_df = 7,
                             stop_words=stopwords.words('english'), ngram_range=ngram_range)
            processed_features = self.vectorizer.fit_transform(self.df[tweet_column_name])
            self.df["processed_features"] = processed_features
            
            # we use the countvectorizer because it allows us to later do feature importance
        else:
            pass
        
        # get rid of all tweets with "no classification" in the classification col
        
        #output_df = self.df[self.df[self.classification_col_name] != None]
        
        """
        self.processed_features_list = []
        self.output = []
        
        for i, output in enumerate(self.df[self.classification_col_name].values[1:]):
            if int(output) in list_of_classes:
                self.processed_features_list.append(processed_features[i])
                self.output.append(self.df[self.classification_col_name].values[i])
        """
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(processed_features, 
                                                                              self.df[self.classification_col_name], 
                                                                              test_size= 0.2)
        
    def random_forest(self, feature_importance = False, plot = False):
        print("Training Classifier")
        rf_clf = RandomForestClassifier(n_estimators=500)
        rf_clf.fit(self.X_train, self.y_train)
        training_score = rf_clf.score(self.X_train, self.y_train)
        accuracy_score = rf_clf.score(self.X_val, self.y_val)
        print("Accuracy Score on Training Data" + str(training_score))
        print("Accuracy Score on Validation Data: " + str(accuracy_score))
        
        if feature_importance:
            vocab = self.vectorizer.vocabulary_

            word_list = list(np.zeros(len(list(vocab.keys()))))
            
            for word in vocab.keys():
                #print(word)
                word_list[vocab[word]] = word
            
            importances = rf_clf.feature_importances_
            
            importances, vocabulary = (list(t) for t in zip(*sorted(zip(importances, word_list))))
            importances.reverse()
            vocabulary.reverse()
            
            if plot:
                        
                plt.bar(vocabulary[:20], importances[:20])
                plt.xticks(rotation=45, fontsize = 13)
                plt.yticks(fontsize = 13)
                plt.title("Most Important Features for Covid-19 Tweets")
                
                plt.xlabel("Feature/Word", fontsize = 13)
                plt.ylabel("Importance", fontsize = 13)
                plt.tight_layout()
            

        
 
headers = ['Unnamed: 0','created_at','id','text','entities','source','user',
           'user.id','username','user.location','user.followers_count',
           'user.friends_count','user.created_at','user.favourites_count',
           'user.statuses_count','user.verified','user.statuses_count2','geo',
           'coordinates','place','retweeted_status.text','retweet_count',
           'tweet_favorite_count','tweet_retweeted','tweet_favorited',
           'Sentiment Polarity', 'Hashtags']
            
x = new_sentiment_analyser(filename, tweet_column_name, headers = headers, classification_col_name="Sentiment Polarity")
#x.find_hashtags()
#x.hashtag_classification_labeler(list_of_hashtag_lists, list_of_classes)
x.clean_tweets()
x.preprocess_data()
x.random_forest(feature_importance = True, plot = True)