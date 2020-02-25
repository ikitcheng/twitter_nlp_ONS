import matplotlib.pyplot as plt
import numpy as np


# TODO: utilities functions
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


# TODO: utilities functions
def tweet_stats(self):
    number_of_tweets = str(
        (self.df["Tweet Type"].to_numpy() == "Tweet").sum())
    number_of_retweets = str(
        (self.df["Tweet Type"].to_numpy() == "Retweet").sum())

    return number_of_tweets, number_of_retweets

        
# TODO: move to utilities - keep a todo comment - unfinished function
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