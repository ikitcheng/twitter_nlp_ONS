import pandas as pd
import os 
from collections import defaultdict
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from nltk.corpus import stopwords
import ast
import numpy as np

dict_of_hashtags = {"eu": ["europeanunion"],
                    "euref": ["eureferendum",
                              "eurefresults",
                              "eurefresult"],
                    "ukref": ["ukreferendum",
                              "ukeureferendum"],
                    "ukexit": ["ukexitseu"]}

class WordCloudGenerator:
    def __init__(self, file_name, headers_file, hashtag, dict_of_hashtags):
        """

        Parameters
        ----------
        file_name : str
            name of the csv file that is to be read in.
        headers_file : str
            name of the csv containing all the csv headers
        hashtag : str
            hashtag of interest. Do not include the #
        dict_of_hashtags : dict
            dictionary of hashtags with similar meanings (as defined by the 
            user). An example would be: 
                    {"eu": ["europeanunion"],
                    "euref": ["eureferendum",
                              "eurefresults",
                              "eurefresult"],
                    "ukref": ["ukreferendum",
                              "ukeureferendum"],
                    "ukexit": ["ukexitseu"]}

        Raises
        ------
        TypeError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        _, fileExtension = os.path.splitext(file_name)
        if fileExtension != '.csv':
            raise TypeError("Data file provided of incorrect type, \n" +
                            "please provide data file of .csv format")
        _, headerFileExtension = os.path.splitext(headers_file)
        if headerFileExtension != '.csv':
            raise TypeError("Header file provided of incorrect type, \n" +
                            "please provide data file of .csv format")

        self.file_name = file_name
        self.headers_file = headers_file
        self.hashtag = hashtag
        
        self.headers = list(pd.read_csv(self.headers_file, sep=',', header = None).values)

        self.df = pd.read_csv(filepath_or_buffer = self.file_name, sep = ",", header = None)
        self.df.columns = self.headers
        self.find_all_hashtags_in_tweet() 
        
    def find_all_hashtags_in_tweet(self):
        """
        Finds all the hashtags in the "entities" column of the dataframe and
        puts them in a new column called "Hashtags"

        Returns
        -------
        None.

        """
        # all the hashtags are in a column called "entities", but we need to clean it up first
        tweet_col = self.df.entities.values
        list_of_hashtags = []
        
        for tweet_info in tweet_col:
            hashtags_for_that_row = []
            for dic in ast.literal_eval(tweet_info[0])["hashtags"]:
                hashtags_for_that_row.append(dic["text"].lower())
            list_of_hashtags.append(hashtags_for_that_row)
        
        self.df['Hashtags']=pd.Series(np.asarray(list_of_hashtags))
            
    def _eliminate_non_ascii(self, dictionary):
        """
        Eliminates all hashtags that are not ascii.
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
    
    def hashtag_freq(self, wordcloud=False, save=False):
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
                
        list_of_hashtag_variations = [self.hashtag, " " + self.hashtag, 
                                      self.hashtag + " ",  " " + self.hashtag + " "]
        
        list_of_words = []
        for i in self.df["Hashtags"].values:
            for j in i[0]:
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
            self.dict_of_words, self.dict_of_hashtags)

        if wordcloud:
            self.gen_wordcloud(save = save)
        return self.dict_of_words
    
    def gen_wordcloud(self, save, show = True):
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
            plt.savefig("Wordclouds/wordcloud-" + self.word_cloud_file + ".png")
        if show:
            plt.show()


        
        
