import pandas as pd
import os
import nltk
import string
import tarfile
import ast
import re
import csv


class cleaner:

    def __init__(self, filename):
        """
        Instantiates a Cleaner object

        Params:
        -------
        str(filename):    path to tar.gz dataset file containing multiple csv files,
                          or path to single csv file
        str(headers):     path to csv file containing column names of dataframe
        """
        self.filename = filename
        with open("all_headers.csv", newline='') as f:
            reader = csv.reader(f)
            headers = [row[0] for row in reader]
        self.headers = headers


    def read_scraped_data(self):
        """
        Reads data scraped from Twitter from a single csv file
        Works only with single csv files

        Returns:
        --------
        df:               dataframe containing csv data
        """
        _, fileExtension = os.path.splitext(self.filename)
        if fileExtension != '.csv':
            raise TypeError("Data file provided of incorrect type, \n" +
                            "please provide data file of .csv format")
        df = pd.read_csv(filepath_or_buffer = self.filename, sep = ",")
        df.columns = self.headers
        return df


    def read_and_merge_scraped_data(self):
        """
        Reads data scraped from Twitter & merges all data into a single dataframe
 
        Returns:
        --------
        dataset:      dataframe containing all concatenated csv files
        """
        _, fileExtension = os.path.splitext(self.filename)
        if fileExtension != '.tar.gz':
            raise TypeError("Data file provided of incorrect type, \n" +
                            "please provide data file of .tar.gz format")
        with tarfile.open(self.filename, "r:*") as tar:
            csv_paths = [file for file in tar.getnames() if file.endswith('.csv')]
            dataset = pd.DataFrame()
            for file in csv_paths:
                try:
                    # there may be 0 hits for any given search
                    current_dataset = pd.read_csv(tar.extractfile(file), header=None, sep=',', low_memory=False)
                except:
                    continue
                dataset = pd.concat([dataset, current_dataset])
            
            dataset.columns = self.headers
            tar.close()
            df = dataset
            return df


    # private method: 
    # _convert_string_to_json_dict converts a string object containing json to a json dict
    def __get_hashtags_list(self, entities_series, json_key):
        list_of_hashtags = ast.literal_eval(entities_series).get(json_key)
        return list_of_hashtags

    # private method:
    # _remove_non_ascii removes strings containing non-ascii characters from a list
    def __remove_non_ascii_and_whitespace(self, list_of_strings):
        list_of_strings[:] = [item for item in list_of_strings if not item.isascii()]
        list_of_strings[:] = [item.strip(' ') for item in list_of_strings]
        list_non_ascii = list_of_strings
        return list_non_ascii


    # example: column = 'entities', json_key = 'hashtags'
    def eliminate_non_ascii_from_json(self, df, column, json_key):
        """
        Eliminates non ascii characters from a column containing a json string
        by specifying the column name and json_key, appends the non-ascii objects
        onto a new column on the dataframe

        Params:
        -------
        df:
        str(column):
        str(json_key):
        """
        df[json_key + '_list'] = df[column].apply(lambda x: self.__get_hashtags_list(x, json_key))
        df[json_key + '_list_non_ascii'] = df[json_key + '_list'].apply(lambda x: self.__remove_non_ascii_and_whitespace(x))
        return df


    # private method: 
    def __remove_frequency_hashtags(self, dictionary, threshold, low=True):
        if low:
            for hashtag in dictionary.keys():
                if dictionary[hashtag] <= threshold:
                    del dictionary[hashtag]
        else:
            for hashtag in dictionary.keys():
                if dictionary[hashtag] >= threshold:
                    del dictionary[hashtag]


    def eliminate_low_freq_hashtags(self, df, threshold):
        # given a column that contains a dict: mapping hashtag to freq
        df['hashtags_low_freq'] = df['hashtags_freq_map'].apply(lambda x: self.__remove_frequency_hashtags(x, threshold))
        return df

    
    def eliminate_high_freq_hashtags(self, df, threshold):
        # given a column that contains a dict: mapping hashtag to freq
        df['hashtags_high_freq'] = df['hashtags_freq_map'].apply(lambda x: self.__remove_frequency_hashtags(x, threshold, low=False))
        return df


    # private method: 
    def __clean_tweet(self, tweet):
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

    def clean_tweet(self, df):
        df['text_cleaned'] = df['text'].apply(lambda x: self.__clean_tweet(x))
        return df