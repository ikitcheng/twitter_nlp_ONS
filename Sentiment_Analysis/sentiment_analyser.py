import numpy as np 
import pandas as pd 
import re
import matplotlib.pyplot as plt
import os
from gensim.parsing.preprocessing import remove_stopwords
import sklearn
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
#from textblob import TextBlob
#import textpreprocessing as tp
#from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.linear_model import LogisticRegression
import joblib
import pickle
from sklearn.naive_bayes import MultinomialNB
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.ensemble import AdaBoostClassifier
from sklearn.datasets import make_classification
import time
from sklearn.neural_network import MLPClassifier
print("hi")

headers_for_basic_files = ["created_at", "id", "text", "entities", "source", 
                           "user.id", "user.screen_name", "user.location", 
                           "user.followers_count", "user.friends_count", 
                           "user.verified", "user.statuses_count", "geo", "coordinates",
                           "place_name", "user_location2", "retweet_count", 
                           "tweet_favorite_count", "tweet_favorited", "tweet_retweeted"]

headers = ["created_at", "id", "text", "entities", "source", 
            "user", "user.id", "username", "user.location", 
            "user.followers_count", "user.friends_count", "user.created_at",
            "user.favourites_count", "user.statuses_count", "user.verified",
            "user.statuses_count2", "geo", "coordinates", "place", "retweeted_status.text", 
            "retweet_count", "tweet_favorite_count", "tweet_retweeted", "tweet_favorited"]


    

class ensemble_sentiment_analyser:
    def __init__(self, training_file_name, training_tweet_column_name, 
                 training_label_col, training_headers,  test_file_name, 
                 test_tweet_column_name, test_columns):
        
        self.training_file_name = training_file_name
        self.training_tweet_column_name = training_tweet_column_name
        self.training_label_col = training_label_col
        self.training_headers = training_headers
        
        self.training_headers = training_headers
        self.test_file_name = test_file_name
        self.test_tweet_column_name = test_tweet_column_name
        self.test_columns = test_columns
        
        print("Reading csv files")
        self.training_df = pd.read_csv(training_file_name, 
                 encoding = "ISO-8859-1", header = None, names = self.training_headers)
        self.training_df = sklearn.utils.shuffle(self.training_df)

        self.test_df = pd.read_csv(test_file_name, header = None, names = self.test_columns)
        
        
        print("Cleaning Training Data")
        self.training_df = self.eliminate_url_from_tweets(self.training_df, self.training_tweet_column_name)
        self.training_df = self.eliminate_twitter_handles(self.training_df, self.training_tweet_column_name)
        self.training_df = self.eliminate_hashtags(self.training_df, self.training_tweet_column_name)
        self.training_df[self.training_tweet_column_name] = self.training_df[self.training_tweet_column_name].map(lambda x: x.lower())
        self.training_df[self.training_tweet_column_name] = self.training_df[self.training_tweet_column_name].map(lambda x: remove_stopwords(x)) # remove stopwords in each tweet
        self.training_df[self.training_tweet_column_name] = self.training_df[self.training_tweet_column_name].str.replace('[^\w\s]','')
        self.training_labels = self.training_df[training_label_col]
        
        print("Cleaning Test Data")
        self.test_df = self.eliminate_url_from_tweets(self.test_df, self.test_tweet_column_name)
        self.test_df = self.eliminate_twitter_handles(self.test_df, self.test_tweet_column_name)
        self.test_df = self.eliminate_hashtags(self.test_df, self.test_tweet_column_name)
        self.test_df[self.test_tweet_column_name] = self.test_df[self.test_tweet_column_name].map(lambda x: x.lower())
        self.test_df[self.test_tweet_column_name] = self.test_df[self.test_tweet_column_name].map(lambda x: remove_stopwords(x)) # remove stopwords in each tweet
        self.test_df[self.test_tweet_column_name] = self.test_df[self.test_tweet_column_name].map(lambda x: x.replace('[^\w\s]',''))
        
        print("Preprocessing Data")
        self.preprocess_data("tfidf", 100000, (1,1)) #10000 features and 400000 tweets gives Accuracy Score of Logistic Regression: 0.7700625
        
        
        
    def eliminate_url_from_tweets(self, dataframe, tweet_col):
        for i, tweet in enumerate(dataframe[tweet_col].values):
            dataframe[tweet_col].values[i] =  re.sub(r'http\S+', '', tweet)
        return dataframe 

    def eliminate_twitter_handles(self, dataframe, tweet_col):
        tokenizer = TweetTokenizer(strip_handles = True)
        for i, tweet in enumerate(dataframe[tweet_col].values):
            tokenized_tweet = tokenizer.tokenize(tweet)
            dataframe[tweet_col].values[i] = ' '.join(tokenized_tweet)
        return dataframe 

    def eliminate_hashtags(self, dataframe, tweet_col):
        for i, tweet in enumerate(dataframe[tweet_col].values):
            dataframe[tweet_col].values[i] =  re.sub(r'#\S+', '', tweet)
        return dataframe 
    
    def preprocess_data(self, vectorizer, number_of_features, ngram_range):
        if vectorizer == "tfidf":
            vectorizer = TfidfVectorizer(max_features=number_of_features, min_df=7,  
                                         stop_words=stopwords.words('english'), 
                                         ngram_range = ngram_range)
        else:
            pass
        
        concatenated_train_test = pd.concat([self.training_df[self.training_tweet_column_name], 
                                             self.test_df[self.test_tweet_column_name]]) # concatenating train and test set for vectorisation

        length_of_train_set = self.training_df[self.training_tweet_column_name].values.size
        length_of_test_set = self.test_df[self.test_tweet_column_name].values.size
        processed_features = vectorizer.fit_transform(concatenated_train_test)#.toarray()
        #pickle.dump(vectorizer, open("vectorizer.pickle", "wb"))
        self.train_data_vectorized = processed_features[:length_of_train_set]
        self.test_data_vectorized = processed_features[length_of_train_set:]
        
    def logistic_regression(self):
        
        print("Hi again!")
        X_train, X_val, y_train, y_val = train_test_split(self.train_data_vectorized, 
                                                            self.training_labels, 
                                                            test_size= 0.2)
        logreg = LogisticRegression()
        logreg = logreg.fit(X_train, y_train)
        predictions_log_reg = []
        for i,tweet in enumerate(self.test_data_vectorized):
            print(i)
            predictions_log_reg.append(logreg.predict(tweet.reshape(-1,1).T)[0])
        
        accuracy_score = logreg.score(X_val,y_val)
        print("Accuracy Score of Logistic Regression: " + str(accuracy_score))
        self.test_df["LogisticSentiment"] = predictions_log_reg
        filename = 'logistic_reg_model.sav'
        joblib.dump(logreg, filename)

        #self.test_df["LogisticSentiment"].to_csv("LogisticSentiment", index = None)
        return predictions_log_reg
    
    
    def naive_bayes(self):
        X_train, X_val, y_train, y_val = train_test_split(self.train_data_vectorized, 
                                                    self.training_labels, 
                                                    test_size= 0.2)
        clf_NB = MultinomialNB().fit(X_train, y_train)
        predictions_NB = []
        for i, feature in enumerate(self.test_data_vectorized):
            #print(i)
            predictions_NB.append(clf_NB.predict(feature.reshape(-1,1).T)[0])
        #predictions_NB = clf.predict(processed_features[number_of_training_samples:])
        training_score = clf_NB.score(X_train, y_train)
        accuracy_score = clf_NB.score(X_val, y_val)
        print("Accuracy Score on Training Data" + str(training_score))
        print("Accuracy Score of Naive Bayes: " + str(accuracy_score))
        filename = 'NB_reg_model.sav'
        joblib.dump(clf_NB, filename)

        #self.test_df["NaiveBayesSentiment"] = predictions_NB
        return accuracy_score
    
    def random_forest(self):
        X_train, X_val, y_train, y_val = train_test_split(self.train_data_vectorized, 
                                            self.training_labels, 
                                            test_size= 0.2)
        
        rf_clf = RandomForestClassifier(n_estimators=50)
        rf_clf.fit(X_train, y_train)
        predictions_rf = []
        for i, feature in enumerate(self.test_data_vectorized):
            #print(i)
            predictions_rf.append(rf_clf.predict(feature.reshape(-1,1).T)[0])
        training_score = rf_clf.score(X_train, y_train)
        accuracy_score = rf_clf.score(X_val, y_val)
        print("Accuracy Score on Training Data" + str(training_score))
        print("Accuracy Score of Random Forest: " + str(accuracy_score))
        self.test_df["RFSentiment"] = predictions_rf
        filename = 'RF_reg_model.sav'
        joblib.dump(rf_clf, filename)

        return accuracy_score
    
    def xgboost(self):
        X_train, X_val, y_train, y_val = train_test_split(self.train_data_vectorized, 
                                    self.training_labels, 
                                    test_size= 0.2)

        data_dmatrix = xgb.DMatrix(data=X_train,label=y_train)
        xg_reg = XGBClassifier(max_depth=6, n_estimators=1000)#objective ='reg:linear', colsample_bytree = 0.3, learning_rate = 0.1,
                    #max_depth = 5, alpha = 10, n_estimators = 10)
        xg_reg.fit(X_train,y_train)

        preds = xg_reg.predict(X_val)
        
        accuracy = accuracy_score(y_val, preds)
        filename = "XGBoost_reg_model.sav"
        joblib.dump(xg_reg, filename)

        print("Accuracy of XGBoost is " + str(accuracy))
        
        return accuracy
    
        
    def nn(self):
        X_train, X_val, y_train, y_val = train_test_split(self.train_data_vectorized, 
                    self.training_labels, 
                    test_size= 0.2)
        clf = MLPClassifier(hidden_layer_sizes=(100, 100, 100), verbose = True) # neural network architecture could be optimised
        clf.fit(X_train, y_train)
        preds = clf.predict(X_val)
        accuracy = accuracy_score(y_val, preds)
        filename = "nn_clf_model.sav"
        joblib.dump(clf, filename)
        print("Accuracy of AdaBoost is " + str(accuracy))
        return accuracy