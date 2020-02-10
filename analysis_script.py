#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 15:44:23 2020

@author: johannesheyl
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
import math
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from nltk.corpus import stopwords
from collections import defaultdict
import ast 
from nltk.stem import WordNetLemmatizer
import nltk
import string
import botometer
import re
import progressbar
from textblob import TextBlob


dict_of_hashtags = {"eu": ["europeanunion"],
                    "euref": ["eureferendum",
                              "eurefresults",
                              "eurefresult"],
                    "ukref": ["ukreferendum",
                              "ukeureferendum"],
                    "ukexit": ["ukexitseu"]}

headers_for_basic_files = ["created_at", "id", "text", "entities", "source", 
                           "user.id", "user.screen_name", "user.location", 
                           "user.followers_count", "user.friends_count", 
                           "user.verified", "user.statuses_count", "geo", "coordinates",
                           "place_name", "user_location2", "retweet_count", 
                           "tweet_favorite_count", "tweet_favorited", "tweet_retweeted"]



class data_analyser:
    def __init__(self, file_name, sheet_name = None):
        self.file_name = file_name
        if self.file_name.endswith(".xlsx"):  
            self.sheet_name = sheet_name
            self.df = pd.read_excel(io=self.file_name, sheet_name=self.sheet_name)
        elif self.file_name.endswith(".csv"):
            self.df = pd.read_csv(filepath_or_buffer = self.file_name, sep = ",")
            self.df.columns = headers_for_basic_files # adding headers at the top
            self.find_all_hashtags_in_tweet() # finds all the hashtags in each tweet and adds a new row
            
    def follower_friend_ratio(self, plot = False):
        
        self.df["Follower-friend ratio"] = self.df["Number of Followers"]/self.df["Number Following"]
        df_np_ffr = self.df["Follower-friend ratio"].to_numpy()
        
        if plot:
            plt.hist(df_np_ffr[np.isfinite(df_np_ffr)],  bins= 1000) #getting rid of any values that are NaN
            plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
            plt.xlabel("Follower-Friend Ratio")
            plt.ylabel("Frequency")
            plt.title("Follower-Friend Ratio for all people who tweeted"
                      "#Brexit on Brexit day")
            plt.xscale('log')
            plt.yscale('log')
    
        return df_np_ffr
    
    def tweet_stats(self):
        number_of_tweets = str(
            (self.df["Tweet Type"].to_numpy() == "Tweet").sum())
        number_of_retweets = str(
            (self.df["Tweet Type"].to_numpy() == "Retweet").sum())

        return number_of_tweets, number_of_retweets
    

    def hashtag_freq(self, list_of_hashtag_variations, ignore=None,
                     wordcloud=False, save=False):
        """
        We want to account for the fact that a single word may be represented
        in multiple ways in a hashtag. For example, the hashtag for "Brexit"
        might be in any one of these forms: ["Brexit ", "brexit ", "BREXIT ",
        " Brexit", " brexit", " BREXIT", "Brexit", "brexit", "BREXIT"].
        Notice that the spaces might be an issue here. We also want to make
        sure we don't accidentally get rid of a hashtag like "#stopbrexit" or
        "#yaytobrexit" just because it has the word Brexit in it. Let me know
        if you guys have any ideas as to how to deal with this,

        Ignore is a list of hashtags that you do not want to include in your
        word cloud. For example, it might be that one hashtag it so common it
        eclipses all the other ones and so the word cloud only shows 1 word.
        """

        list_of_words = []
        for i in self.df["Hashtags"]:
            if isinstance(i, str):
                for j in list_of_hashtag_variations:
                    if j in i:
                        # if a tweet has more than one hashtag, we want to get
                        # rid of the one that we already have, i.e.: Brexit -->
                        # we want to see what other hashtags use GIVEN that
                        # someone tweets #Brexit
                        i = i.replace(j, "")
                list_of_words.append(i)
            elif type(i) == list: # this is for the case when each entry is a list (this happens when we have to manually create a "Tweets" column)
                for j in i:
                    if j not in list_of_hashtag_variations:
                        list_of_words.append(j)

        self.updated_list = []
        for num, i in enumerate(list_of_words):
            if i:  # empty string same as False
                i = i.strip()  # get rid of white space
                for j in i.split():
                    self.updated_list.append(j.lower())

        self.dict_of_words = defaultdict(int)
        for w in self.updated_list:
            self.dict_of_words[w] += 1

        # first let's get rid of non-ascii content
        self._eliminate_non_ascii(self.dict_of_words)
        self._eliminate_one_off_hashtags(self.dict_of_words)
        self._combine_hashtags_that_are_the_same(
            self.dict_of_words, dict_of_hashtags)

        if wordcloud:
           # updated_list_as_string = " ".join(list(dict_of_words.keys())) # need to turn list of words into a string for WordCloud
            #updated_list_as_string = " ".join(self.updated_list)
            updated_list_as_string = ""
            if ignore is not None:
                for word in ignore:
                    del self.dict_of_words[word]
            for word in self.dict_of_words.keys():
                updated_list_as_string = updated_list_as_string + \
                    (word + " ") * self.dict_of_words[word]

            # removing the extra blank space at the beginning
            updated_list_as_string = updated_list_as_string.lstrip()

            wordcloud = WordCloud(
                relative_scaling=0.5,
                # set or space-separated string
                stopwords=set(stopwords.words("english")), collocations=False
            ).generate(updated_list_as_string)
            fig = plt.figure(figsize=(12, 10), facecolor='w', edgecolor='k')
            plt.imshow(wordcloud)
            plt.axis("off")
            if save:
                plt.savefig("wordcloud.jpg")
            plt.show()
        return self.dict_of_words

    def _eliminate_non_ascii(self, dictionary):
        """
        Eliminates all hashtags that are no ascii.
        """
        keys_to_be_deleted = [
        ]  # can't delete keys from dictionary in for loop as dictionary size changing
        for key in dictionary.keys():
            if not key.isascii():
                keys_to_be_deleted.append(key)
        for key in keys_to_be_deleted:
            del dictionary[key]

    def _eliminate_one_off_hashtags(self, dictionary):
        """
        Eliminates hashtags that occur fewer than five times
        """
        for key in list(dictionary):
            if dictionary[key] <= 5:
                del dictionary[key]

    def _combine_hashtags_that_are_the_same(self, dictionary, hashtag_dict):
        """
        Combines hashtags that are basically the same.
        Need to provide a dictionary that tells you which hashtags are the 
        same, i.e.: {euref: [eureferendum, "eurefer"]}
        """

        hashtags_to_be_deleted = []

        for dups in hashtag_dict.values():
            hashtags_to_be_deleted = hashtags_to_be_deleted + dups

        for hashtag in hashtag_dict.keys():
            corresponding_equivalent_hashtags = hashtag_dict[hashtag]
            for i in corresponding_equivalent_hashtags:
                dictionary[hashtag] += dictionary[i]

        for i in hashtags_to_be_deleted:
            del dictionary[i]
            
        return dictionary 
            
    def find_all_hashtags_in_tweet(self):
        # all the hashtags are in a column called "entities", but we need to clean it up first
        
        tweet_col = self.df.entities.values
        list_of_hashtags = []
        
        for tweet_info in tweet_col:
            hashtags_for_that_row = []
            for dic in ast.literal_eval(tweet_info)["hashtags"]:
                hashtags_for_that_row.append(dic["text"].lower())
            list_of_hashtags.append(hashtags_for_that_row)
        
        self.df['Hashtags']=pd.Series(np.asarray(list_of_hashtags))
            
    
    


    def _stem(self, dictionary):
        """
        Still need to figure out how to do this properly!

        """
        dictionary_with_identical_starts = {}
        for i in dictionary:
            dictionary_with_identical_starts[i] = []
            for j in dictionary:
                if i != j and i.startswith(j):
                    dictionary_with_identical_starts[i].append(j)
        # now get rid of empty dictionaries
        identical_keys = []
        corresponding_identical_words = []

        for i in dictionary_with_identical_starts.keys():
            if len(dictionary_with_identical_starts[i]) != 0:
                identical_keys.append(i)
                corresponding_identical_words.append(
                    dictionary_with_identical_starts[i])
                
                

    def gen_wordcloud(self, dict_of_words, save=False):
        """
        Input: list_of_words
        output: wordcloud
        """
        string_of_words = ""
        for word in self.dict_of_words.keys():
            string_of_words = string_of_words + \
                (word + " ") * self.dict_of_words[word]
        wordcloud = WordCloud(relative_scaling=0.5,
                              stopwords=set(STOPWORDS),
                              collocations=False
                              ).generate(string_of_words)

        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()
        if save:
            plt.savefig("wordcloud.jpg")
            
    def clean_tweet(self, tweet):
        """
        Input: tweet (originial)
        output: tweet without RT tag, username and urls, punctuation
        """

        # remove url
        clean_tweet = re.sub(r"http\S+", "", tweet)
        # remove @username
        clean_tweet = re.sub(r"@\S+", "", clean_tweet)
        # remove RT
        clean_tweet = re.sub(r"RT", "", clean_tweet)
        # remove #hastags
        clean_tweet = re.sub(r"#\S+", "", clean_tweet)
        # remove punctuation
        tokens = [word.lower() for sent in nltk.sent_tokenize(clean_tweet) for
                  word in nltk.word_tokenize(sent)]
        filtered_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens,
        # raw punctuation)
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
        clean_tweet = ' '.join(filtered_tokens)
        return clean_tweet.lower()

    def sentiment_analysis(self, list_of_tweets):
        """
        Input: list_of_tweets
        output: sentiments = [polarity, subjectivity]
        """
        nTweets = len(list_of_tweets)
        sentiments = np.zeros([nTweets, 2])
        for i, tweet in enumerate(list_of_tweets):
            t = TextBlob(tweet)
            p, s = t.sentiment
            sentiments[i] = [p, s]
        return sentiments

    def BotOrNot(self, username, authentication):
        """
        Input: username = twitter handle
               Authentication = [consumerKey, consumerSecret,
                                 accessToken, accessTokenSecret,
                                 rapidapiKey]
        Output: 1 = bot, 0 = not bot
        """

        twitter_app_auth = {
            'consumer_key': authentication[0],
            'consumer_secret': authentication[1],
            'access_token': authentication[2],
            'access_token_secret': authentication[3]}

        bom = botometer.Botometer(wait_on_ratelimit=True,
                                  rapidapi_key=authentication[4],
                                  **twitter_app_auth)

        result = bom.check_account(username)
        # if bot score> 0.43: bot = 1 else: 0 threshold setting:
        # https://www.pewresearch.org/internet/2018/04/09/bots-in-the-twittersphere-methodology/
        if (result['cap']['universal'] > 0.5) or \
           (result['scores']['universal'] > 0.43):
            return 1
        else:
            return 0


x = data_analyser("ScrapingTwitterRealTime/datasets/scrape_data_2020-01-28-2020-01-29/brexit.csv")
x.hashtag_freq(['Brexit ','brexit ', 'BREXIT ', ' Brexit',' brexit', ' BREXIT','Brexit','brexit', 'BREXIT'], wordcloud=True)#
        
#x = data_analyser("NewsaboutbrexitonTwitter.xlsx", "Table1-1")
#x.hashtag_freq(['Brexit ','brexit ', 'BREXIT ', ' Brexit',' brexit', ' BREXIT','Brexit','brexit', 'BREXIT'], wordcloud=True)#

y = excel_analyser("NewsaboutbrexitonTwitter.xlsx", "Table1-1")
y.hashtag_freq(['Brexit ',
                'brexit ',
                'BREXIT ',
                ' Brexit',
                ' brexit',
                ' BREXIT',
                'Brexit',
                'brexit',
                'BREXIT'],
               wordcloud=False)
y.gen_wordcloud(x.dict_of_words, True)