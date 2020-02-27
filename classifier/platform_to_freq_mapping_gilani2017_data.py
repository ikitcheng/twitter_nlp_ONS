import pandas as pd
from ScrapeTwitterTimeline_FeatureExtraction import scrape_user_timeline
from bs4 import BeautifulSoup as soup
import re
import unicodedata
import csv


def strip_html(tweet):
    tweet = soup(tweet, 'html.parser').text
    tweet = unicodedata.normalize("NFKD", tweet)
    # return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 
    return tweet


df = pd.read_csv('user_features_labels_noNan.csv', index_col=0) 
usernames = list(df.index)


username_source_df = pd.DataFrame(columns=['username', 'source_freq_map'])

for username in usernames:
    print(username)
    userdata = scrape_user_timeline(int(username), 200) # list of dictionaries
    userdata_df = pd.DataFrame(userdata, index=range(len(userdata)))
    counts = {}
    if 'source' in userdata_df.columns:
        userdata_df['source_without_html'] = userdata_df['source'].apply(lambda x: strip_html(x))
        counts = userdata_df['source_without_html'].value_counts().to_dict()
    username_source_df = username_source_df.append({'username' : username , 'source_freq_map' : counts}, ignore_index=True)

username_source_df.to_csv("username_source_freq_mapping.csv")
