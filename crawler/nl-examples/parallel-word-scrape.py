from twitterscraper import query_tweets
import datetime
import pandas as pd
from multiprocessing import Pool
from argparse import ArgumentParser
import datetime as dt
import sys

global twitter_tweet_info
twitter_tweet_info = []

def get_tweet_info(tweet):

    twitter_tweet_info = {}
    twitter_tweet_info["screen_name"] = tweet.screen_name
    twitter_tweet_info["username"] = tweet.username
    twitter_tweet_info["user_id"] = tweet.user_id
    twitter_tweet_info["tweet_id"] = tweet.tweet_id
    twitter_tweet_info["tweet_url"] = tweet.tweet_url
    twitter_tweet_info["timestamp"] = tweet.timestamp
    twitter_tweet_info["timestamp_epochs"] = tweet.timestamp_epochs
    twitter_tweet_info["is_quoted_tweet"] = tweet.is_quoted_tweet
    twitter_tweet_info["text"] = tweet.text
    twitter_tweet_info["text_html"] = tweet.text_html
    twitter_tweet_info["links"] = tweet.links
    twitter_tweet_info["hashtags"] = tweet.hashtags
    twitter_tweet_info["quoted_user"] = tweet.quoted_user
    twitter_tweet_info["quoted_text"] = tweet.quoted_text
    twitter_tweet_info["has_media"] = tweet.has_media
    twitter_tweet_info["img_urls"] = tweet.img_urls
    twitter_tweet_info["video_url"] = tweet.video_url
    twitter_tweet_info["likes"] = tweet.likes
    twitter_tweet_info["retweets"] = tweet.retweets
    twitter_tweet_info["replies"] = tweet.replies
    twitter_tweet_info["is_replied"] = tweet.is_replied
    twitter_tweet_info["is_reply_to"] = tweet.is_reply_to
    twitter_tweet_info["parent_tweet_id"] = tweet.parent_tweet_id
    twitter_tweet_info["reply_to_users"] = tweet.reply_to_users

    # source - android
    # is retweet
    # country code
    # place attributes - place full_name, type, bounding box

    return twitter_tweet_info


def main():

    parser = ArgumentParser(
        description="Scrape twitter for a query")
    # parser.add_argument(
    #     '--query',
    #     '-q',
    #     help="sql form i.e. 'Trump OR Hilary'")
    parser.add_argument(
        '--since',
        '-s',
        help='beginning of time period to scrape twitter data')
    parser.add_argument(
        '--until',
        '-u',
        help='end of time period to scrape twitter data')
    parser.add_argument(
        '--lang',
        '-l',
        help='language to scrape twitter')
    parser.add_argument(
        '--limit',
        '-i',
        help='number of reponses to return')
    parser.add_argument(
        '--file',
        '-f',
        help='file to save data')


    args = parser.parse_args()
    # query = args.query
    since = args.since
    until = args.until
    lang = args.lang
    limit = args.limit
    filename = args.file

    queries =["covid OR covid19 OR covid_19 OR coronavirus OR coronavirusupdate",
              "coronavirusoutbreak OR coronavirusupdates OR covid19uk OR coronavirusuk",
              "COVID2019 OR corona virus OR stayhome OR stayathome OR lockdown",
              "stayhomechallenge OR staysafe OR quarantineandchill OR covididiots OR nhs",
              "socialdistancing OR pandemic OR stayhomestaysafe OR panicbuying OR outbreak",
              "treatments OR epidemic OR immunity OR immune OR asymptomatic", 
              "flattenthecurve OR testtracetrack OR symptom OR coronapocalypse OR covidiots",
              "nhs OR hospital OR mypandemicsurvivalplan OR togetherathome OR extendlockdown OR herdimmunity" ] 

    since_date = dt.datetime.strptime(since, '%Y-%m-%d').date()
    until_date = dt.datetime.strptime(until, '%Y-%m-%d').date()


    for i, query in enumerate(queries):

        file_name = "" + str(i) + "-" + lang + "-" + filename

        tweets = query_tweets(query=query,
                            begindate=since_date,
                            enddate=until_date,
                            poolsize=20,
                            lang=lang,
                            limit=int(limit))

        pool = Pool(8)
        for tweet in pool.map(get_tweet_info, tweets):
            twitter_tweet_info.append(tweet)

        cols = ['screen_name', 'username', 'user_id', 'tweet_id', 'tweet_url', 'timestamp', 'timestamp_epochs', 'is_quoted_tweet',
                'text', 'text_html', 'links', 'hashtags', 'quoted_user', 'quoted_text', 'has_media', 'img_urls', 'video_url',
                'likes', 'retweets', 'replies', 'is_replied', 'is_reply_to', 'parent_tweet_id', 'reply_to_users']
        data_frame = pd.DataFrame(twitter_tweet_info, columns=cols)
        data_frame.to_csv(file_name)


if __name__ == '__main__':
    main()
