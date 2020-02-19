import pandas as pd
import os
import csv
import re
import nltk
import string
from argparse import ArgumentParser


class Cleaner:

    def __init__(self, filename, headers):
        _, fileExtension = os.path.splitext(filename)
        if fileExtension != '.csv':
            raise TypeError("Data file provided of incorrect type, \n" +
                            "please provide data file of .csv format")
        self.filename = filename
        self.df = pd.read_csv(filepath_or_buffer = self.filename, sep = ",")

        # with open(headers) as csv_file:
        #     csv_reader = csv.reader(csv_file, delimiter=',')
        #     self.headers = [header for header in csv_reader]
        #     print(headers)
        # self.df.columns = headers # adding headers at the top


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


    def clean_tweet(self, tweet):
        """
        Input: tweet (original)
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


parser = ArgumentParser(
        description="Execute sentiment analysis and generate word clouds from provided twitter data file")
parser.add_argument(
        '--filename',
	'-f',
        help="file containing twitter data")
parser.add_argument(
        '--headers',
	'-H',
        help="file containing twitter attribute headers")

args = parser.parse_args()
filename = args.filename
headers = args.headers

# x = DataAnalyser("../Scraper/datasets/Brexit/All_Headers/scrape_data_2020-01-29-2020-01-30/brexit.csv")
cleaned_data = Cleaner(filename, headers)
print(cleaned_data.df.head())
print(cleaned_data.df['user.location'])