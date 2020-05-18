# parallel user timeline scrape

from twitterscraper.query import query_user_info, query_tweets_from_user
import pandas as pd
from multiprocessing import Pool
import sys

global twitter_user_info
twitter_user_info = []


def get_user_info(twitter_user):
    """
    An example of using the query_user_info method
    :param twitter_user: the twitter user to capture user data
    :return: twitter_user_data: returns a dictionary of twitter user data
    """
    user_info = query_user_info(user=twitter_user)
    twitter_user_data = {}
    twitter_user_data["user"] = user_info.user                    # feature: screen_name_length
    twitter_user_data["fullname"] = user_info.full_name           # user name
    twitter_user_data["location"] = user_info.location            # feature: location
    twitter_user_data["blog"] = user_info.blog                    # feature: url
    twitter_user_data["date_joined"] = user_info.date_joined      # feature: age
    twitter_user_data["id"] = user_info.id                        # twitter account id
    twitter_user_data["num_tweets"] = user_info.tweets            # feature: statuses_count
    twitter_user_data["following"] = user_info.following          # feature: friends_count
    twitter_user_data["followers"] = user_info.followers          # feature: followers_count
    twitter_user_data["likes"] = user_info.likes                  # feature: favourites_count
    twitter_user_data["lists"] = user_info.lists                  # feature: listed_count
    #twitter_user_data["is_verified"] = user_info.is_verified
    twitter_user_data["description"] = user_info.description

    # verified
    # quoted tweets

    max_num_tweets = 10
    latest_tweets = query_tweets_from_user(twitter_user, limit=max_num_tweets)      # list of 200 tweet objects
    tweets, tweets_html, hashtags, has_media, num_retweets, num_likes, links, num_replies, reply_to_users, timestamp_epochs, is_quoted_tweet, quoted_user, quoted_text, = get_tweet_attribute(latest_tweets)

    twitter_user_data["tweets"] = tweets
    twitter_user_data["tweets_html"] = tweets_html
    twitter_user_data["hashtags"] = hashtags
    twitter_user_data["has_media"] = has_media
    twitter_user_data["num_retweets"] = num_retweets
    twitter_user_data["num_likes"] = num_likes
    twitter_user_data['links'] = links
    twitter_user_data['num_replies'] = num_replies
    twitter_user_data['reply_to_users'] = reply_to_users
    twitter_user_data['timestamp_epochs'] = timestamp_epochs
    twitter_user_data['is_quoted_tweet'] = is_quoted_tweet
    #twitter_user_data['is_retweet'] = is_retweet
    twitter_user_data['quoted_user'] = quoted_user
    twitter_user_data['quoted_text'] = quoted_text
    #twitter_user_data['retweet_user'] = retweet_user
    #twitter_user_data['retweet_text'] = retweet_text
    
    return twitter_user_data


def get_tweet_attribute(tweet_objects):
    tweets, tweets_html, hashtags, has_media = [], [], [], []
    num_retweets, num_likes, links = [], [], []
    num_replies, reply_to_users, timestamp_epochs = [], [], []
    is_quoted_tweet, quoted_user, quoted_text = [], [], []
    
    for tweet in tweet_objects:
        tweets.append(tweet.text)
        tweets_html.append(tweet.text_html)
        hashtags.append(tweet.hashtags)
        has_media.append(tweet.has_media)
        num_retweets.append(tweet.retweets)
        num_likes.append(tweet.likes)
        links.append(tweet.links)
        num_replies.append(tweet.replies)
        reply_to_users.append(tweet.reply_to_users)
        timestamp_epochs.append(tweet.timestamp_epochs)
        is_quoted_tweet.append(tweet.is_quoted_tweet)
        #is_retweet.append(tweet.is_retweet)
        quoted_user.append(tweet.quoted_user)
        quoted_text.append(tweet.quoted_text)
        #retweet_user.append(tweet.retweet_user)
        #retweet_text.append(tweet.retweet_text)
    
    return tweets, tweets_html, hashtags, has_media, num_retweets, num_likes, links, num_replies, reply_to_users, timestamp_epochs, is_quoted_tweet, quoted_user, quoted_text


def scrape_timeline(usernames, filename):
    users = []

    for user in usernames:
        users.append(user)

    pool_size = len(users)
    if pool_size < 8:
        pool = Pool(pool_size)
    else:
        pool = Pool(8)

    for user in pool.map(get_user_info, users):
        twitter_user_info.append(user)

    cols = ['id', 'fullname', 'date_joined', 'location', 'blog', 'num_tweets', 'following', 'followers', 'likes',
            'lists', 'description', 'tweets', 'hashtags', 'has_media', 'num_retweets', 'num_likes', 'links', 'num_replies', 'reply_to_users',
            'timestamp_epochs', 'is_quoted_tweet', 'is_retweet', 'quoted_user', 'quoted_text', 'retweet_user', 'retweet_text']
    data_frame = pd.DataFrame(twitter_user_info, index=users, columns=cols)
    data_frame.index.name = "Users"
    data_frame.sort_values(by="followers", ascending=False, inplace=True, kind='quicksort', na_position='last')
    data_frame.to_csv(filename)
    return data_frame


def main():
    users = ['masalakeri', 'jk_rowling']
    filename = "here"
    scrape_timeline(users, filename)

if __name__ == '__main__':
    main()
