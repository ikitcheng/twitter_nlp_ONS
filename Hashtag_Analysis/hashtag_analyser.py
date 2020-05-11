#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 19:17:03 2020

@author: johannesheyl
"""

import ast
from collections import defaultdict
import numpy as np
from scipy.optimize import curve_fit


class hashtag_analyser:
    def __init__(self, df):
        self.df = df
        
    
        
    def find_all_hashtags_in_tweet(self, df):
        """
        Finds all the hashtags in the "entities" column of the dataframe and
        puts them in a new column called "Hashtags"
        Returns
        -------
        None.
        """
        # all the hashtags are in a column called "entities", but we need to clean it up first
        tweet_col = df.entities.values
        list_of_hashtags = []
        
        for i, tweet_info in enumerate(tweet_col):
            #print(i)
            hashtags_for_that_row = []
            for dic in ast.literal_eval(tweet_info)["hashtags"]:
                hashtags_for_that_row.append(dic["text"].lower())
            list_of_hashtags.append(hashtags_for_that_row)
        
        
        self.df["Hashtags"] = list_of_hashtags

        list_of_hashtags = [item for sublist in list_of_hashtags for item in sublist] # flattening list of lists
        
        
        return list_of_hashtags
    
    
    def order_hashtags(self, hashtag_list):
        """
        

        Parameters
        ----------
        hashtag_list : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        fq = defaultdict(int)
        for w in hashtag_list:
            fq[w] += 1
        freq_list = []
        sorted_hashtag_list = np.asarray(sorted(fq, key=fq.get, reverse=True))
        for i in sorted_hashtag_list:
            freq_list.append(fq[i])
        index_list = np.arange(len(sorted_hashtag_list)) + 1
        
        return np.asarray(index_list), np.asarray(sorted_hashtag_list), np.asarray(freq_list)

        
    def zipf_exponent(self, index_list, freq_list):
        def power_law(x, a, b):
            return a*x**b

        popt, pcov = curve_fit(power_law, index_list, freq_list)
        zipf_exponent = popt[1]
        
        percentage_of_tweets_with_top_ten_hashtags = 1-10**(zipf_exponent+1) #zipf exponent is always negative
        
        print("The top ten most used hashtags in this dataset are used in " + str(percentage_of_tweets_with_top_ten_hashtags * 100) + "% of tweets." )
        
        return zipf_exponent
    
    
    


    
