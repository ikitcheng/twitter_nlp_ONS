"""
Created on Tues Feb 04 2020

@author: nlad
"""

import tweepy
import os
import json
import csv
import yaml
import datetime
from argparse import ArgumentParser


parser = ArgumentParser(
        description="Scrape twitter API for a hashtag")
parser.add_argument(
        '--hashtag',
	'-t',
        help="hashtag to scrape for")
parser.add_argument(
        '--filename',
        '-f',
        help='output csv file to save twitter data')
parser.add_argument(
        '--since',
        '-s',
        help='beginning of time period to scrape twitter data')
parser.add_argument(
        '--until',
        '-u',
        help='end of time period to scrape twitter data')
parser.add_argument(
        '--config',
        '-c',
        help='config file containing twitter api authentication')


# grab command line args
args = parser.parse_args()
hashtag = '#' + args.hashtag
filename = args.filename
config = args.config
since = args.since
until = args.until


with open(config, 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


# handle authentication
consumer_key = cfg['consumerKey']
consumer_secret = cfg['consumerSecret']
access_token = cfg['accessToken']
access_token_secret = cfg['accessTokenSecret']
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth,wait_on_rate_limit=True)


# open/create a file to append data
if os.path.exists(filename):
        append_write = 'a' # append if already exists
else:
        append_write = 'w' # make a new file if not
csvFile = open(filename, append_write)
csvWriter = csv.writer(csvFile)


def on_status(status):
    tweet = ""
    
    if hasattr(status, 'retweeted_status'):
        try:
            tweet = status.retweeted_status.extended_tweet["full_text"]
        except:
            tweet = status.retweeted_status.text
    else:
        try:
            tweet = status.extended_tweet["full_text"]
        except AttributeError:
            tweet = status.text
    
    return tweet



endTime = datetime.datetime.now() + datetime.timedelta(minutes=20)
for i, tweet in enumerate(tweepy.Cursor(api.search,q=hashtag,count=200,
                           lang="en",
                           since=since,
                           until=until).items()):

    tweets_encoded = tweet.text.encode('utf-8')
    tweets_decoded = tweets_encoded.decode('utf-8')
    csvWriter.writerow([tweet.created_at, tweet.id, tweets_decoded, 
                        tweet.entities, tweet.source, tweet.user,
                        tweet._json["user"]["id"], 
                        tweet._json["user"]["screen_name"], 
                        tweet._json["user"]["location"], 
                        tweet._json["user"]["followers_count"], 
                        tweet._json["user"]["friends_count"],
                        tweet._json["user"]["created_at"],
                        tweet._json["user"]["favourites_count"],
                        tweet._json["user"]["statuses_count"],
                        tweet._json["user"]["verified"], 
                        tweet._json["user"]["statuses_count"],
                        tweet.coordinates if tweet.coordinates else None, 
                        tweet.place.name if tweet.place else None, 
                        on_status(tweet),
                        tweet.retweet_count, tweet.favorite_count, 
                        tweet.retweeted,
                        tweet.favorited if tweet.favorited else None,
                        ])

    if i % 1000 == 0:
        print("Tweet " + str(i) + " created at: " + str(tweet.created_at) + " saved")
    if datetime.datetime.now() >= endTime:
       break

