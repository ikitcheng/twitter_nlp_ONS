import tweepy
import csv
import pandas as pd
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
        '--config',
        '-c',
        help='config file containing twitter api authentication')
args = parser.parse_args()

hashtag = '#' + args.hashtag
filename = args.filename
config = args.config

with open(config, 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

consumer_key = cfg['consumerKey']
consumer_secret = cfg['consumerSecret']
access_token = cfg['accessToken']
access_token_secret = cfg['accessTokenSecret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)

# Open/Create a file to append data
csvFile = open(filename, 'a')
csvWriter = csv.writer(csvFile)

endTime = datetime.datetime.now() + datetime.timedelta(minutes=20)
for i, tweet in enumerate(tweepy.Cursor(api.search,q=hashtag,count=100,
                           lang="en",
                           since="2020-01-30",
                           until="2020-02-01").items()):
    csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])
    if i % 1000 == 0:
        print("Tweet " + str(i) + " created at: " + str(tweet.created_at) + " saved")
    if datetime.datetime.now() >= endTime:
       break
