# -*- coding: utf-8 -*-
"""
Created on Mon May 11 13:43:48 2020

@author: I Kit Cheng
"""

from ScrapeTwitterTimeline_FeatureExtraction import scrape_user_timeline, check_invalid_user
import json
import pandas as pd
import datetime
import time
import ast

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

if __name__ == '__main__':
    
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
    
    N = 200 # number of tweets to scrape per user (max 200)
    
    folder = 'timeline_data/'
    fname = 'timeline_data.csv'
    headers = ['screen_name','userid','timeline']
    df = pd.DataFrame(columns=headers)
    start = time.time()
    for i, user in enumerate(users[0:2]):
        print()
        print(f'{i+1}/{len(users)}')
        print('-' * 3)
        print(user)
        
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
        
        screen_name = data[0]['user']['screen_name']
        userid = data[0]['user']['id']
        
        row_df = pd.DataFrame([[screen_name,userid,data]], columns=headers)
        df = pd.concat([row_df, df], ignore_index=True)
        if i == 0:
            row_df.to_csv(f'{folder}{fname}', mode='a', header=headers,
                          index=False)
        else:
            row_df.to_csv(f'{folder}{fname}', mode='a', header=False,
                          index=False)
