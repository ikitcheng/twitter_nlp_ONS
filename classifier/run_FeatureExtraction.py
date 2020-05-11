# -*- coding: utf-8 -*-
"""
Created on Mon May 11 16:39:30 2020

@author: I Kit Cheng
"""
from ScrapeTwitterTimeline_FeatureExtraction import main_FeatureExtraction
import pandas as pd
import ast

def literal_eval(timeline):
    return ast.literal_eval(timeline)

if __name__ == '__main__':
    # load saved timeline_data.csv
    folder = 'timeline_data/'
    fname = 'timeline_data.csv'
    df = pd.read_csv(f'{folder}{fname}')
    df['timeline'] = df['timeline'].apply(lambda x: literal_eval(x))
    
    for i, data in enumerate(df.timeline.to_list()):
        main_FeatureExtraction(data, i)
