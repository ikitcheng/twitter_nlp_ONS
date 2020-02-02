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
from wordcloud import WordCloud
from nltk.corpus import stopwords
from collections import defaultdict

class excel_analyser:
    def __init__(self, file_name, sheet_name):
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.excel_df = pd.read_excel(io=self.file_name, sheet_name=self.sheet_name)
        
    def follower_friend_ratio(self, plot = False):
        
        self.excel_df["Follower-friend ratio"] = self.excel_df["Number of Followers"]/self.excel_df["Number Following"]
        excel_np_ffr = self.excel_df["Follower-friend ratio"].to_numpy()
        
        if plot:
            plt.hist(excel_np_ffr[np.isfinite(excel_np_ffr)],  bins= 1000) #getting rid of any values that are NaN
            plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
            plt.xlabel("Follower-Friend Ratio")
            plt.ylabel("Frequency")
            plt.title("Follower-Friend Ratio for all people who tweeted #Brexit on Brexit day")
            plt.xscale('log')
            plt.yscale('log')
    
        return excel_np_ffr
    
    def tweet_stats(self):
        number_of_tweets = str((self.excel_df["Tweet Type"].to_numpy() == "Tweet").sum())
        number_of_retweets = str((self.excel_df["Tweet Type"].to_numpy() == "Retweet").sum())
        
        return number_of_tweets, number_of_retweets
    
    def hashtag_freq(self, list_of_hashtag_variations, wordcloud = False, save = False):
        """
        We want to account for the fact that a single word may be represented in multiple ways in a hashtag. For example, the hashtag for "Brexit"
        might be in any one of these forms: ["Brexit ", "brexit ", "BREXIT ", " Brexit", " brexit", " BREXIT", "Brexit", "brexit", "BREXIT"]. Notice that 
        the spaces might be an issue here. We also want to make sure we don't accidentally get rid of a hashtag like "#stopbrexit" or "#yaytobrexit" just 
        because it has the word Brexit in it. Let me know if you guys have any ideas as to how to deal with this. 
        """
        
        list_of_words = []
        for i in self.excel_df["Hashtags"]:
            if type(i) == str:
                for j in list_of_hashtag_variations:
                    if j in i:
                        i = i.replace(j, "") # if a tweet has more than one hashtag, we want to get rid of the one that we already have, i.e.: Brexit --> we want to see what other hashtags use GIVEN that someone tweets #Brexit
                list_of_words.append(i)

        updated_list = []        
        for num, i in enumerate(list_of_words):
            if i: # empty string same as False
                i = i.strip() # get rid of white space
                for j in i.split():
                    updated_list.append(j.lower())
        
        dict_of_words= defaultdict( int )
        for w in updated_list:
            dict_of_words[w] += 1     
            
            
            
        if wordcloud:
            updated_list_as_string = " ".join(updated_list) # need to turn list of words into a string for WordCloud

            wordcloud = WordCloud(
                      relative_scaling = 1.0,
                      stopwords = set(stopwords.words("english")) # set or space-separated string
                      ).generate(updated_list_as_string)
            fig=plt.figure(figsize=(12, 10), facecolor='w', edgecolor='k')
            plt.imshow(wordcloud)
            plt.axis("off")
            if save:
                plt.savefig("wordcloud")
            plt.show()
        
        return dict_of_words
    
x = excel_analyser("NewsaboutbrexitonTwitter.xlsx", "Table1-1")
x.hashtag_freq(list_of_hashtag_variations=["Brexit ", "brexit ", "BREXIT ", " Brexit", " brexit", " BREXIT", "Brexit", "brexit", "BREXIT"])["clottedcreampalm"]