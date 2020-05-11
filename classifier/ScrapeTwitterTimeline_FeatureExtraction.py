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
from bs4 import BeautifulSoup as soup
import unicodedata
import time
from textdistance import levenshtein


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

    if isinstance(user, str):
        params = dict(screen_name=user,
                      count=N,
                      include_rts=1)
    elif isinstance(user, int):
        params = dict(user_id=user,
                      count=N)

    with open('config.yaml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    token = cfg['bearerToken']
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(url=url, params=params, headers=headers)
    print(resp)
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
        Whether the user provided a location associated with their profile.
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
            verified)  # , bot_in_name, bot_in_des)

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

        # or data[i]['is_quote_status']):  # a retweet or quote
        elif ('retweeted_status' in data[i].keys()): # a retweet
            fav_count_retweets.append(data[i]['favorite_count'])

        elif not data[i]['is_quote_status']: # not a quote, then it's an original tweet
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

        # or data[i]['is_quote_status']):  # post is a retweet -maybe should
        # include quoted retweets
        elif ('retweeted_status' in data[i].keys()): # a retweet 
            ret_count_retweets.append(data[i]['retweet_count'])

        elif not data[i]['is_quote_status']:  # post not a quote so original tweet
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
        Average time period (in seconds) between posts of any type.
    Tavg_tweet: float
        Average time period (in seconds) between tweets.
    Tavg_ret: float
        Average time period (in seconds) between retweets.
    Tavg_quote: float
        Average time period (in seconds) between retweets with comments.
    Tavg_reply: float
        Average time period (in seconds) between replies.
    screen_name_len: int
        Screen name length.
    age: float
        The number of seconds since the launch of twitter to the time of
        account creation. Larger means created more recently.
    levenshtein_name_screen_name: int
        Levenshtein metric for similarity between 'name' and 'screen_name'.

    """
    #
    nPostMention = 0
    nPostPlace = 0
    nPostTweet = 0
    nPostRet = 0
    nPostQuote = 0
    nPostReply = 0

    for i in range(len(data)):  # for each post
        if data[i]['entities']['user_mentions']:
            nPostMention += 1

        if data[i]['place']:
            nPostPlace += 1

        if (isinstance(data[i]['in_reply_to_status_id'], int)):  # a reply
            nPostReply += 1

        elif ('retweeted_status' in data[i].keys()):  # a retweet
            nPostRet += 1

        elif data[i]['is_quote_status']:  # a retweet with a comment
            nPostQuote += 1

        else:  # an original tweet
            nPostTweet += 1
    ##
    t1 = data[len(data) - 1]['created_at']
    t2 = data[0]['created_at']
    datetime1 = datetime.datetime.strptime(t1, '%a %b %d %H:%M:%S %z %Y')
    datetime2 = datetime.datetime.strptime(t2, '%a %b %d %H:%M:%S %z %Y')

    Tinterval = (datetime2 - datetime1).total_seconds()
    Tavg = Tinterval / len(data)

    if nPostTweet != 0:
        Tavg_tweet = Tinterval / nPostTweet
    else:
        Tavg_tweet = np.nan

    if nPostRet != 0:
        Tavg_ret = Tinterval / nPostRet
    else:
        Tavg_ret = np.nan

    if nPostQuote != 0:
        Tavg_quote = Tinterval / nPostQuote
    else:
        Tavg_quote = np.nan

    if nPostReply != 0:
        Tavg_reply = Tinterval / nPostReply
    else:
        Tavg_reply = np.nan

    # Twitter launch time
    t1 = 'Sat Jul 15 00:00:00 +0000 2006'
    datetime1 = datetime.datetime.strptime(t1, '%a %b %d %H:%M:%S %z %Y')
    t2 = data[0]['user']['created_at']
    datetime2 = datetime.datetime.strptime(t2, '%a %b %d %H:%M:%S %z %Y')
    age = (datetime2 - datetime1).total_seconds()

    ##
    screen_name_len = (len(data[0]['user']['screen_name']))

    ##
    levenshtein_name_screen_name = levenshtein(data[0]['user']['screen_name'],
                                               data[0]['user']['name'])
    return (nPostMention, nPostQuote, nPostPlace,
            Tavg, Tavg_tweet, Tavg_ret, Tavg_quote, Tavg_reply,
            age, screen_name_len, levenshtein_name_screen_name)


def strip_html(tweet):
    tweet = soup(tweet, 'html.parser').text
    tweet = unicodedata.normalize("NFKD", tweet)
    # return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z
    # \t])|(\w+:\/\/\S+)", " ", tweet).split())
    return tweet


def get_source_frequency_mapping(data):
    userdata_df = pd.DataFrame(data, index=range(len(data)))
    counts = {}
    if 'source' in userdata_df.columns:
        userdata_df['source_without_html'] = userdata_df['source'].apply(
            lambda x: strip_html(x))
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


def main_FeatureExtraction(data, i, fname='user_features_0.csv'):
    headers = ['username',
               'userid',
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
               'Tavg_tweet',
               'Tavg_ret',
               'Tavg_quote',
               'Tavg_reply',
               'age',
               'screen_name_len',
               'levenshtein_name_screen_name']
    df = pd.DataFrame(columns=headers)
    
    username = data[0]['user']['screen_name']
    userid = data[0]['user']['id']

    #counts = get_source_frequency_mapping(data)
    #username_source_df = username_source_df.append({'username' : username , 'source_freq_map' : counts}, ignore_index=True)

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
    nPostMention, nPostQuote, nPostPlace,\
        Tavg, Tavg_tweet, Tavg_ret, Tavg_quote, Tavg_reply, age,\
        screen_name_len,\
        levenshtein_name_screen_name = get_statistical_features(
            data)

    username_features = [username,
                         userid,
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
                         Tavg_tweet,
                         Tavg_ret,
                         Tavg_quote,
                         Tavg_reply,
                         age,
                         screen_name_len,
                         levenshtein_name_screen_name]

    row_df = pd.DataFrame([username_features], columns=headers)
    df = pd.concat([row_df, df], ignore_index=True)
    if i == 0:
        row_df.to_csv(f'user_features/{fname}', mode='a', header=headers,
                      index=False)
    else:
        row_df.to_csv(f'user_features/{fname}', mode='a', header=False,
                      index=False)
    return df

def main(users, N, fname='user_features_0.csv'):
    """

    Parameters
    ----------
    users : list
        A list of Twitter usernames.
    N : int
        Number of most recent posts of each user.
    fname: str
        Output filename.

    Returns
    -------
    Dataframe of features. Each row is a user, and each column is a feature.

    """
    df = pd.DataFrame()
    start = time.time()
    for i, user in enumerate(users):
        print()
        print(f'{i+1}/{len(users)}')
        print('-' * 3)
        if (i + 1) % 1500 == 0:
            time_taken = time.time() - start
            print(f'Requests made: {i+1} requests made')
            print(f'Time taken: {time_taken/60} mins')
            if time_taken > 930:
                print('Passed 15min window, keep scraping!')
                pass
            else:
                print('Sleeping until 15mins reached')
                # api limit: 1500 requests/ 15min (1000s just to be safe)
                time.sleep(930 - time_taken)
                start = time.time()

        data = scrape_user_timeline(user, N)
        if check_invalid_user(data):
            continue
        row_df = main_FeatureExtraction(data,i,fname)
        df = pd.concat([row_df, df], ignore_index=True)
    return df

# In[]:
if __name__ == '__main__':
    ##
    # Demo scrape and feature extraction
    ##
    start = time.time()

    # number of tweets to scrape per user (max 200)
    N = 200

    # known bot accounts
    users = [
        'year_progress',
        'grow_slow',
        'softlandscapes',
        'deepquestionbot',
        'thinkpiecebot',
        'I_Find_Planets',
        'tiny_star_field',
        'EmojiAquarium',
        'tinycarebot']

    print('Scraping user timelines: ')
    
    df_features = main(users, N)

    print('Complete!')
    print(f'Time elapsed: {time.time()-start:.2f} s')
