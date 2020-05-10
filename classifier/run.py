
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 19:20:05 2020

@author: I Kit Cheng
"""
from ScrapeTwitterTimeline_FeatureExtraction import main
from cleaning_feature_df import drop_duplicates, replaceNans
from classify_new_bots_orgs import load_trained_model
import time
import os
import pandas as pd

# In[]:
###########################################
# SCRAPE USER TIMELINES FOR FEATURE DF
###########################################
# input files should be (daily) csvs with all hashtags combined using
# read_tar.py
folder = 'scraped_data/'
files = os.listdir(folder)

start = time.time()
for i, file in enumerate(files):
    print(f'file: {file}\n')
    N = 200  # number of posts to scrape from user timeline
    df = pd.read_csv(f'{folder}{file}')
    df = drop_duplicates(df, 'username')
    users = df.username.to_list()
    print('Scraping user timelines:')
    print('-' * 24)
    # default: scrape first 10 users
    df_features = main(users[0:10], N, fname=file)

    print('Complete!')
    print(f'Time elapsed: {time.time()-start:.2f} s\n')


###########################################
# CLEAN FEATURE DF
###########################################
#folder = 'user_features/'
#files = os.listdir(folder)

    # print(file)
    #df_features = pd.read_csv(f'{folder}{file}')
    print('Cleaning feature df:')
    print('-' * 20)
    df_features['Tavg_tweet'][df_features['Tavg_reply'].isna()] = 1e10
    df_features['Tavg_ret'][df_features['Tavg_reply'].isna()] = 1e10
    df_features['Tavg_quote'][df_features['Tavg_reply'].isna()] = 1e10
    df_features['Tavg_reply'][df_features['Tavg_reply'].isna()] = 1e10
    df_features = replaceNans(df_features, strategy='median')
    df_features = df_features.drop(columns=['userid'])
    df_features.to_csv(f'user_features/noNan_{file}', index=False)
    print('Complete!')
    print(f'Time elapsed: {time.time()-start:.2f} s\n')

###########################################
# CLASSIFY FEATURE DF
###########################################
#folder = 'user_features_noNan/'
#files = os.listdir(folder)

    # print(file)
    #df = pd.read_csv(f'{folder}{file}')
    #df_features = drop_duplicates(df_features, col='username')
    print('Classifying users:')
    print('-' * 18)
    df_features.index = df_features.pop('username')
    model = load_trained_model(
        'fine_tunned_models/xgb_classifier_human_bot_org_colab.pkl')
    pred = model.predict(df_features)
    classifications = {'labels': pred}
    df_classify = pd.DataFrame(classifications, columns=['labels'])
    df_classify.index = df_features.index
    print('Complete!')
    print(f'Time elapsed: {time.time()-start:.2f} s\n')

###########################################
# MERGE LABELS TO SCRAPED DATA
###########################################
    df_merge = pd.merge(df_classify, df, on='username')
    df_merge.to_csv(f'user_labels/{file}')
