# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 02:06:49 2020

@author: I Kit Cheng
"""
import numpy as np
import pandas as pd
import requests
import datetime
import yaml
import progressbar
from bs4 import BeautifulSoup as soup
import unicodedata

def scrape_user_timeline(user, N):
    """

    Parameters
    ----------
    user : string or int
        Twitter screen_name or Twitter user_id.
    N : int
        Number of most recent posts of each user.

    Returns
    -------
    data : list
        A list of dictionaries, each dictionary is a Tweet object. 
        https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object

    """

    # twitter api endpoint
    url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    
    if isinstance(user,str):
        params = dict(screen_name=user,
                      count=N)
    elif isinstance(user,int):
        params = dict(user_id=user,
                      count=N)
    
    with open('config.yaml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
    token = cfg['bearerToken']
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(url=url, params=params, headers=headers)
    data = resp.json()
    return data


# In[]:

################################## Features ##################################

# Metadata of user profile

def get_user_numerical_features(data):
    """

    Parameters
    ----------
    data : list
        A list of dictionaries, each dictionary is a Tweet object. 

    Returns
    -------
    nFollowers : int
        Number of followers.
    nFollowings : int
        Number of followings. 
    FollowersToFollowing : float
        Number of followers / Number of followings.
    nLists : int
        Number of public lists the user is a member of.
    nFavs : int
        Number of tweets the user has liked.
    nPosts : int
        Total number of posts.

    """
    user = data[0]['user']
    nFollowers = user['followers_count']
    nFollowings = user['friends_count']
    try:
        FollowersToFollowing = nFollowers / nFollowings
    except ZeroDivisionError:
        FollowersToFollowing = np.nan

    # 
    nLists = user['listed_count']
    nFavs = user['favourites_count']  
    nPosts = user['statuses_count']  
    return (nFollowers, nFollowings, FollowersToFollowing, nLists,
            nFavs, nPosts)

def get_user_binary_features(data):
    """

    Parameters
    ----------
    data : list
        A list of dictionaries, each dictionary is a Tweet object. 

    Returns
    -------
    geo_enabled : bool
        Whether the user enabled geo-tagging.
    location_provided : bool
        Whether the user provided a location associated with the post.
    url_provided : bool
        Whether the user has an URL in association with their profile.
    description_provided : bool
        Whether the profile has a description.
    verified : bool
        Whether the account is verified.

    """
    user = data[0]['user']
    geo_enabled = int(user['geo_enabled'])
    location_provided = int(len(user['location']) is not 0)
    url_provided = int(user['url'] is not None)
    description_provided = int(len(data[0]['user']['description']) is not 0)
    verified = int(user['verified'])
    #bot_in_name_position = int(data[0]['user']['screen_name'].lower().find('bot'))
    # if bot_in_name_position == -1:
    #     bot_in_name = 0
    # else: bot_in_name = 1

    # bot_in_des_position = int(data[0]['user']['description'].lower().find('bot'))
    # if bot_in_des_position == -1:
    #     bot_in_des = 0
    # else: bot_in_des = 1
    return (geo_enabled, location_provided, url_provided, description_provided,
            verified)#, bot_in_name, bot_in_des)

# In[]:
# Popularity of post feature

# retweeted_status attribute contains representation of the ORIGINAL Tweet
# N.B. each post by the user can be an original tweet, a retweet or a reply

def fav(data, P):
    """
    
    Parameters
    ----------
    data : list
        A list of dictionaries, each dictionary is a Tweet object.
    P : string
        Type of post: 'tweets', 'retweets' or 'replies'

    Returns
    -------
    int
        Number of users favoring the post P of the user.

    """

    fav_count_tweets = []
    fav_count_retweets = []
    fav_count_replies = []

    for i in range(len(data)):  # for each post
        if (isinstance(data[i]['in_reply_to_status_id'], int)):  # a reply
            fav_count_replies.append(data[i]['favorite_count'])

        elif ('retweeted_status' in data[i].keys()): #or data[i]['is_quote_status']):  # a retweet or quote 
            fav_count_retweets.append(data[i]['favorite_count'])

        else:  # an original tweet
            fav_count_tweets.append(data[i]['favorite_count'])

    if P == 'replies':
        return sum(fav_count_replies), len(fav_count_replies)

    elif P == 'retweets':
        return sum(fav_count_retweets), len(fav_count_retweets)

    elif P == 'tweets':
        return sum(fav_count_tweets), len(fav_count_tweets)


def ret(data, P):
    """

    Parameters
    ----------
    data : list
        A list of dictionaries, each dictionary is a Tweet object.
    P : string
        Type of post: 'tweets', 'retweets' or 'replies'

    Returns
    -------
    int
        Number of users retweeting the post of the user.

    """

    ret_count_tweets = []
    ret_count_retweets = []
    ret_count_replies = []

    for i in range(len(data)):  # for each post
        if (isinstance(data[i]['in_reply_to_status_id'], int)):  # a reply
            ret_count_replies.append(data[i]['retweet_count'])

        elif ('retweeted_status' in data[i].keys()): # or data[i]['is_quote_status']):  # post is a retweet
            ret_count_retweets.append(data[i]['retweet_count'])

        else:  # post is an original tweet
            ret_count_tweets.append(data[i]['retweet_count'])

    if P == 'replies':
        return sum(ret_count_replies), len(ret_count_replies)

    elif P == 'retweets':
        return sum(ret_count_retweets), len(ret_count_retweets)

    elif P == 'tweets':
        return sum(ret_count_tweets), len(ret_count_tweets)


def pop_fav(data, P, nFollowings):
    """

    Parameters
    ----------
    data : list
        A list of dictionaries, each dictionary is a Tweet object.
    P : string
        Type of post: 'tweets', 'retweets' or 'replies'
    nFollowings : int
        Number of followings.

    Returns
    -------
    float
        Popularity score of the user's posts based on likes.

    """

    s, n = fav(data, P)
    try:
        Likes_popularity_score = s / n / nFollowings
    except ZeroDivisionError:
        #print(f'There are no {P} in the data...')
        return np.nan
    return Likes_popularity_score


def pop_ret(data, P, nFollowings):
    """

    Parameters
    ----------
    data : list
        A list of dictionaries, each dictionary is a Tweet object.
    P : string
        Type of post: 'tweets', 'retweets' or 'replies'
    nFollowings : int
        Number of followings.

    Returns
    -------
    float
        Popularity score of the user's posts based on retweets.

    """

    s, n = ret(data, P)
    try:
        Retweets_popularity_score = s / n / nFollowings
    except ZeroDivisionError:
        #print(f'There are no {P} in the data...')
        return np.nan
    return Retweets_popularity_score


# In[]:

# Statistical features

def get_statistical_features(data):
    """

    Parameters
    ----------
    data : list
        A list of dictionaries, each dictionary is a Tweet object. 
        https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object

    Returns
    -------
    nPostMention : int
        Number of posts that contain a mention to another user.
    nPostQuote : int
        Number of quoted tweets (i.e. retweets with a comment).
    nPostPlace : int
        Number of posts that were posted in association with a place 
        (geo-tagged tweet).
    Tavg : float
        Average time interval (in seconds) between tweets.

    """

    nPostMention = 0
    nPostQuote = 0
    nPostPlace = 0

    for i in range(len(data)):  # for each post
        if data[i]['entities']['user_mentions']:
            nPostMention += 1
    
        if data[i]['is_quote_status']:
            nPostQuote += 1
            
        if data[i]['place']:
            nPostPlace += 1

    t1 = data[len(data) - 1]['created_at']
    t2 = data[0]['created_at']
    datetime1 = datetime.datetime.strptime(t1, '%a %b %d %H:%M:%S %z %Y')
    datetime2 = datetime.datetime.strptime(t2, '%a %b %d %H:%M:%S %z %Y')

    Tinterval = (datetime2 - datetime1).total_seconds()
    Tavg = Tinterval / len(data)
    if Tavg == 0:
        Tavg = np.nan
      
    # Twitter launch time
    t1 = 'Sat Jul 15 00:00:00 +0000 2006'
    datetime1 = datetime.datetime.strptime(t1, '%a %b %d %H:%M:%S %z %Y')
    t2 = data[0]['user']['created_at']
    datetime2 = datetime.datetime.strptime(t2, '%a %b %d %H:%M:%S %z %Y')
    age = (datetime2 - datetime1).total_seconds()
    
    username = data[0]['user']['screen_name']
    screen_name_len = (len(data[0]['user']['screen_name']))

    return (nPostMention, nPostQuote,
            nPostPlace, Tavg, age, screen_name_len)

def strip_html(tweet):
    tweet = soup(tweet, 'html.parser').text
    tweet = unicodedata.normalize("NFKD", tweet)
    # return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 
    return tweet

def get_source_frequency_mapping(data):
    userdata_df = pd.DataFrame(data, index=range(len(data)))
    counts = {}
    if 'source' in userdata_df.columns:
        userdata_df['source_without_html'] = userdata_df['source'].apply(lambda x: strip_html(x))
        counts = userdata_df['source_without_html'].value_counts().to_dict()
    return counts
# In[]:
def check_invalid_user(data):
    if len(data) == 0:
        print('No posts found.')
        return True
    elif (isinstance(data, dict)) and ('errors' in data.keys()):
        print('User does not exist.')
        return True
    elif (isinstance(data, dict)) and ('error' in data.keys()):
        print('Account suspended.')
        return True
    
        
def main(users, N):
    """
    
    Parameters
    ----------
    users : list
        A list of Twitter usernames.
    N : int
        Number of most recent posts of each user.

    Returns
    -------
    Dataframe of features. Each row is a user, and each column is a feature. 

    """
    users_data_dict = {}

    bar = progressbar.ProgressBar(max_value=len(users))
    counter = 0
    
    username_source_df = pd.DataFrame(columns=['username', 'source_freq_map'])  # source_freq_mapping
    
    for user in users:
        counter += 1
        bar.update(counter)

        #print(f'\nScraping: {user}')
        data = scrape_user_timeline(user, N)
        if check_invalid_user(data):
            continue
        username = data[0]['user']['screen_name']
        userid = data[0]['user']['id']
        
        counts = get_source_frequency_mapping(data)
        username_source_df = username_source_df.append({'username' : username , 'source_freq_map' : counts}, ignore_index=True)
        
        # user features
        nFollowers, nFollowings, FollowersToFollowing, nLists, nFavs, nPosts = get_user_numerical_features(
            data)
        geo, location, url, description, verified = get_user_binary_features(
            data)

        # tweet features
        fav_tweets = fav(data, 'tweets')
        fav_retweets = fav(data, 'retweets')
        fav_replies = fav(data, 'replies')

        ret_tweets = ret(data, 'tweets')
        ret_retweets = ret(data, 'retweets')
        ret_replies = ret(data, 'replies')

        pop_fav_tweets = pop_fav(data, 'tweets', nFollowings)
        pop_fav_retweets = pop_fav(data, 'retweets', nFollowings)
        pop_fav_replies = pop_fav(data, 'replies', nFollowings)

        pop_ret_tweets = pop_ret(data, 'tweets', nFollowings)
        pop_ret_retweets = pop_ret(data, 'retweets', nFollowings)
        pop_ret_replies = pop_ret(data, 'replies', nFollowings)

        # other features
        nPostMention, nPostQuote, nPostPlace, Tavg, age, screen_name_len = get_statistical_features(
            data)
        
        users_data_dict[username] = [userid,
                                     nFollowers,
                                    nFollowings,
                                    FollowersToFollowing,
                                    nLists,
                                    nFavs,
                                    nPosts,
                                    geo,
                                    location,
                                    url,
                                    description,
                                    verified,
                                    fav_tweets[0],
                                    fav_retweets[0],
                                    fav_replies[0],
                                    ret_tweets[0],
                                    ret_retweets[0],
                                    ret_replies[0],
                                    pop_fav_tweets,
                                    pop_fav_retweets,
                                    pop_fav_replies,
                                    pop_ret_tweets,
                                    pop_ret_retweets,
                                    pop_ret_replies,
                                    nPostMention,
                                    nPostQuote,
                                    nPostPlace,
                                    Tavg,
                                    age,
                                    screen_name_len]
    
    df = pd.DataFrame.from_dict(users_data_dict, orient='index')
    
    try:
        df.columns = ['userid',
                      'nFollowers',
                    'nFollowings',
                    'FollowersToFollowing',
                    'nLists',
                    'nFavs',
                    'nPosts',
                    'geo',
                    'location',
                    'url',
                    'description',
                    'verified',
                    'fav_tweets',
                    'fav_retweets',
                    'fav_replies',
                    'ret_tweets',
                    'ret_retweets',
                    'ret_replies',
                    'pop_fav_tweets',
                    'pop_fav_retweets',
                    'pop_fav_replies',
                    'pop_ret_tweets',
                    'pop_ret_retweets',
                    'pop_ret_replies',
                    'nPostMention',
                    'nPostQuote',
                    'nPostPlace',
                    'Tavg',
                    'age',
                    'screen_name_len']
    except ValueError:
        df.columns = []
        
    df.index.name = 'username'                                            
    df.to_csv('user_features.csv')
    username_source_df.to_csv('username_source_freq_mapping1.csv')
    return df, username_source_df

# In[]:
if __name__ == '__main__':
    from get_usernames import get_usernames
    N = 200  # number of posts to scrape from user timeline
    users = get_usernames('../../Datasets/user_classification/ind_vs_bot/brexitday/brexitday.csv')
    # users = ['tinycarebot','EmojiAquarium','tiny_star_field','I_Find_Planets',
    #          'thinkpiecebot','deepquestionbot','softlandscapes','pixelsorter',
    #          'grow_slow','year_progress']
    #ground_truth_df = pd.read_csv('../../Datasets/user_classification/ind_vs_bot/dataset_human_bot_ground_truth.csv')
    #users = ground_truth_df.username
    
    df, username_source_df = main(users, N)
# In[]:
    # clean tweet function
    #def clean_tweet(tweet):
    #    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())       