import pandas as pd
import os
import ast
import numpy as np
from collections import defaultdict
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import re
from nltk.tokenize import TweetTokenizer
import string
from nltk.corpus import stopwords

s=set(stopwords.words('english'))

dict_of_hashtags = {"eu": ["europeanunion"],
                    "euref": ["eureferendum",
                              "eurefresults",
                              "eurefresult"],
                    "ukref": ["ukreferendum",
                              "ukeureferendum"],
                    "ukexit": ["ukexitseu"]}

class WordCloudGenerator:
    def __init__(self, file_name, tweet_col):
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
        self.file_name = file_name
        #self.hashtag = hashtag
        #self.headers = headers_for_basic_files#list(pd.read_csv(self.headers_file, sep=',', header = None).values)

        self.df = pd.read_csv(filepath_or_buffer = self.file_name, sep = ",")
        #self.df.columns = self.headers
        #self.find_all_hashtags_in_tweet() 
        self.df["date"] = self.df["created_at"].str[:10]
        
        self.eliminate_url_from_tweets()
        print("URLs eliminated!")
        self.eliminate_twitter_handles()
        print("Twitter Handles eliminated!")
        self.eliminate_hashtags()
        print("Hashtags Eliminated!")
        self.eliminate_punctuation()
        print("Punctuation Eliminated!")
        self.make_lowercase()
        print("Tweets are now lowercase!")
        
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
            for dic in ast.literal_eval(tweet_info)["hashtags"]:
                hashtags_for_that_row.append(dic["text"].lower())
            list_of_hashtags.append(hashtags_for_that_row)
        
        self.df['Hashtags']=pd.Series(np.asarray(list_of_hashtags))
        
    def eliminate_url_from_tweets(self):
        tweet_col = "text"
        for i, tweet in enumerate(self.df[tweet_col].values):
            self.df[tweet_col].values[i] =  re.sub(r'http\S+', '', tweet)

    def eliminate_twitter_handles(self):
        tweet_col = "text"
        tokenizer = TweetTokenizer(strip_handles = True)
        for i, tweet in enumerate(self.df[tweet_col].values):
            tokenized_tweet = tokenizer.tokenize(tweet)
            self.df[tweet_col].values[i] = ' '.join(tokenized_tweet)

    def eliminate_hashtags(self):
        tweet_col = "text"
        for i, tweet in enumerate(self.df[tweet_col].values):
            self.df[tweet_col].values[i] =  re.sub(r'#\S+', '', tweet)
        #return dataframe 
            
    def eliminate_punctuation(self):
        tweet_col = "text"
        #self.df[tweet_col] = self.df[tweet_col].str.replace('[^\w\s]','')
        self.df[tweet_col] = self.df[tweet_col].str.replace('[^\w\s]','')
        #return dataframe 

        #df['review'].str.replace('[^\w\s]','')
            
    def make_lowercase(self):
        tweet_col = "text"
        self.df[tweet_col] = self.df[tweet_col].map(lambda x: x.lower())


            
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
            if dictionary[key] <= 10:
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
                
        #list_of_hashtag_variations = [self.hashtag, " " + self.hashtag, 
         #                             self.hashtag + " ",  " " + self.hashtag + " "]
        list_of_words = []
        for i in self.df["Hashtags"].values:
            for j in i:
                #if j not in list_of_hashtag_variations:
                list_of_words.append(j)

        self.updated_list = []
        for num, i in enumerate(list_of_words):
            if i:  # empty string same as False
                if type(i) == str:
                    i = i.strip()  # get rid of white space
                    for j in i.split():
                        self.updated_list.append(j.lower())

        self.dict_of_words = defaultdict(int)
        for w in self.updated_list:
            self.dict_of_words[w] += 1

        # first let's get rid of non-ascii content
        self._eliminate_non_ascii(self.dict_of_words)
        self._eliminate_one_off_hashtags(self.dict_of_words)
        #self._combine_hashtags_that_are_the_same(
          #  self.dict_of_words, self.dict_of_hashtags)

        if wordcloud:
            self.gen_wordcloud(save = save)
        return self.dict_of_words
    
    def word_freq(self, wordcloud=False, save=False):
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
                
        #list_of_hashtag_variations = [self.hashtag, " " + self.hashtag, 
         #                             self.hashtag + " ",  " " + self.hashtag + " "]
        list_of_words = []
        for i in self.df["text"].values:
            list_of_words.append(i) # put all words in list

        self.updated_list = []
        for num, i in enumerate(list_of_words):
            if i:  # empty string same as False
                if type(i) == str:
                    i = i.strip()  # get rid of white space
                    for j in i.split():
                        if j not in s: # check we are not including stopwords
                            self.updated_list.append(j.lower())

        self.dict_of_words = defaultdict(int)
        for w in self.updated_list:
            self.dict_of_words[w] += 1 # increasing the frequency of the word in the dictionary by 1

        # first let's get rid of non-ascii content
        #self._eliminate_non_ascii(self.dict_of_words)
        self._eliminate_one_off_hashtags(self.dict_of_words)

        if wordcloud:
            self.gen_wordcloud(save = save)
        del self.dict_of_words["rt"] # don't care about retweetss
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
        wordcloud = WordCloud(width=800, height=400, relative_scaling=0.5,
                              stopwords=set(STOPWORDS),
                              collocations=False
                              ).generate(string_of_words)
        #plt.figure( )
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()
        if save:
            plt.savefig("wordcloud-" + save + ".png")
        if show:
            plt.show()



# covid_file = "/Users/johannesheyl/Dropbox/PhD/Group_Project/csv_files_for_sentiment_and_location/User-based_wordclouds/Coronavirus_scrape_data_sentiment_labels.csv"

# x = WordCloudGenerator(covid_file, "text")
# t = x.word_freq()
# x.gen_wordcloud("covid_entire_dataset", show = False)
