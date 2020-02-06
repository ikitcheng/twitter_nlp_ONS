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


def scrape_user_timeline(user, N):
    """
    Scrape the latest N posts from user timeline.
    Inputs: user (string)
            N (int)

    Output: tweet objects (https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object)
    """

    # twitter api endpoint
    url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

    params = dict(
        screen_name=user,
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
# In[]:
# Metadata of user profile

def get_user_numerical_features(data):
    user = data[0]['user']
    nFollowers = user['followers_count']
    nFollowings = user['friends_count']
    FollowersToFollowing = nFollowers / nFollowings

    # number of public lists this user is a member of
    nLists = user['listed_count']
    nFavs = user['favourites_count']  # number of tweets this user has ‘liked’
    nPosts = user['statuses_count']  # total number of posts
    return [
        nFollowers,
        nFollowings,
        FollowersToFollowing,
        nLists,
        nFavs,
        nPosts]


def get_user_binary_features(data):
    user = data[0]['user']
    geo_enabled = user['geo_enabled']
    location_provided = len(user['location']) is not 0
    url_provided = user['url'] is not None
    description_provided = len(data[0]['user']['description']) is not 0
    verified = user['verified']
    return [geo_enabled, location_provided, url_provided, description_provided,
            verified]


# In[]:
# Popularity of post feature

# retweeted_status attribute contains representation of the ORIGINAL Tweet
# premium features: reply_count
# N.B. each post by the user can be an original tweet, a retweet or a reply

def fav(data, P):
    """
    Number of users liking the post of the user
    Input: P = 'tweets', 'retweets' or 'replies'
    """
    fav_count_tweets = []
    fav_count_retweets = []
    fav_count_replies = []

    for i in range(len(data)):  # for each post
        if (isinstance(data[i]['in_reply_to_status_id'], int)
            ):  # post is a reply
            fav_count_replies.append(data[i]['favorite_count'])

        elif ('retweeted_status' in data[i].keys()):  # post is a retweet
            fav_count_retweets.append(data[i]['favorite_count'])

        else:  # post is an original tweet
            fav_count_tweets.append(data[i]['favorite_count'])

    if P == 'replies':
        return sum(fav_count_replies), len(fav_count_replies)

    elif P == 'retweets':
        return sum(fav_count_retweets), len(fav_count_retweets)

    elif P == 'tweets':
        return sum(fav_count_tweets), len(fav_count_tweets)


def ret(data, P):
    """
    Number of users retweeting the post of the user
    Input: P = 'tweets', 'retweets' or 'replies'
    """

    ret_count_tweets = []
    ret_count_retweets = []
    ret_count_replies = []

    for i in range(len(data)):  # for each post
        if (isinstance(data[i]['in_reply_to_status_id'], int)):  # a reply
            ret_count_replies.append(data[i]['retweet_count'])

        elif ('retweeted_status' in data[i].keys()):  # post is a retweet
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
    Popularity of user based on likes

    Input: P = 'tweets', 'retweets' or 'replies'
           nFollowings = number of followings of the user

    Output: Likes_popularity_score (float)
    """
    s, n = fav(data, P)
    try:
        Likes_popularity_score = s / n / nFollowings
    except ZeroDivisionError:
        print(f'There are no {P} in the data...')
        return np.nan
    return Likes_popularity_score


def pop_ret(data, P, nFollowings):
    """
    Popularity of user based on retweets

    Input: P = 'tweets', 'retweets' or 'replies'
           nFollowings = number of followings of the user

    Output: Retweets_popularity_score (float)
    """
    s, n = ret(data, P)
    try:
        Retweets_popularity_score = s / n / nFollowings
    except ZeroDivisionError:
        print(f'There are no {P} in the data...')
        return np.nan
    return Retweets_popularity_score


# In[]:

# Statistical features

def get_statistical_features(data):
    # number of posts that contain a mention to
    # another user
    nPostMention = 0
    nPostQuote = 0
    nPostPlace = 0

    for i in range(len(data)):  # for each post
        if data[i]['entities']['user_mentions']:
            nPostMention += 1

    # number of quoted tweets (i.e. retweets with
    # a comment)
        if data[i]['is_quote_status']:
            nPostQuote += 1

    # number of posts that were posted in
    # association with a place (geo-tagged tweet)
        if data[i]['place']:
            nPostPlace += 1

    # average interval between tweets
    t1 = data[len(data) - 1]['created_at']
    t2 = data[0]['created_at']
    datetime1 = datetime.datetime.strptime(t1, '%a %b %d %H:%M:%S %z %Y')
    datetime2 = datetime.datetime.strptime(t2, '%a %b %d %H:%M:%S %z %Y')

    Tinterval = (datetime2 - datetime1).total_seconds()
    try:
        Tavg = len(data) / Tinterval
    except ZeroDivisionError:
        print("Time interval is 0 between first "
              "and last post.")
        Tavg = np.nan

    # can't find attribute with this information.
    return (nPostMention, nPostQuote,
            nPostPlace, Tavg)


# In[]:
if __name__ == '__main__':
    N = 10  # number of posts to scrape from user timeline
    users = ['ikitcheng', 'nlad95']
    df = pd.DataFrame(columns=['nFollowers',
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
                               'Tavg'],
                      index=users)
    for user in users:
        print(f'\nScraping: {user}')
        data = scrape_user_timeline(user, N)
        if len(data) == 0:
            continue
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
        nPostMention, nPostQuote, nPostPlace, Tavg = get_statistical_features(
            data)

        df.loc[user] = [nFollowers,
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
                        Tavg]
    df.to_csv('users_features.csv')
