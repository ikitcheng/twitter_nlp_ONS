import json
import os 
from collections import defaultdict
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from nltk.corpus import stopwords
import ast
import numpy as np
from collections import Counter
from itertools import chain


class wordcloudgenerator:
    def __init__(self, df, filename):
        """
        df: cleaned dataframe!!!
        """
        # todo: if instance cleaner
        self.df = df
        self.similar_hashtags = json.loads(filename)
 
    
    # i.e. column = 'hashtags_list_non_ascii' 
    def hashtag_freq(self, column, combine_similar=False, **kwargs):
        """
        Returns a dictionary of the frequency of each hashtag. Hashtags that
        are considered to be similar (as defined by self.dict_of_hashtags) are 
        combined. 
        
        Parameters
        ----------
        wordcloud : Boolean
            if True, a wordcloud is generated using the gen_wordcloud function.
        save : Boolean
            if True, the generated wordcloud is saved

        Returns
        -------
        self.dict_of_words: dict
            dictionary of hashtag frequency.

        """
        similar_hashtags_dict = kwargs.get('similar_hashtags_dict', None)
        # TODO:
        #if similar_hashtags:
            # call a lambda on combine_hashtags function
            # and send in as argument similar_hashtags_dict

        self.df['hashtags_freq_dict'] = self.df[column].apply(lambda x: self._word_list_to_freq_dict(x))
        hashtag_freq_dict =  Counter(chain.from_iterable(self.df['hashtags_from_dict']))
        self.hashtags_freq_dict = dict(hashtag_freq_dict)


    def _word_list_to_freq_dict(self, wordlist):
        wordfreq = [wordlist.count(word) for word in wordlist]
        return dict(list(zip(wordlist,wordfreq)))


    def gen_wordcloud(self, save=False, show=True, **kwargs):
        """

        Parameters
        ----------
        save : Boolean
            if True, wordcloud is saved.
        show : Boolean, optional
            if True, the wordcloud is displaced

        Returns
        -------
        None.

        """
        word_cloud_file = kwargs.get('word_cloud_file', None)
        string_of_words = ""
        for word in self.hashtags_freq_dict.keys():
            string_of_words = string_of_words + \
                (word + " ") * self.hashtags_freq_dict[word]
        wordcloud = WordCloud(relative_scaling=0.5,
                              stopwords=set(STOPWORDS),
                              collocations=False
                              ).generate(string_of_words)

        plt.imshow(wordcloud)
        plt.axis("off")
        if save:
            plt.savefig("Wordclouds/wordcloud-" + word_cloud_file + ".png")
        if show:
            plt.show()


    # TODO:
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
        
