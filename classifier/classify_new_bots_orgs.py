# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 21:32:26 2020

@author: I Kit Cheng
"""
from cleaning_feature_df import main_cleaning
import pickle
import pandas as pd

def load_trained_model(model_pkl_file):
    model_pkl = open(model_pkl_file,'rb')
    model = pickle.load(model_pkl)
    return model

if __name__ == '__main__':
    csv_file = '../../Datasets/user_classification/scraped_data/brexitday/user_features_new.csv'
    df = main_cleaning(csv_file)
    model_org = load_trained_model('rf_org_classifier_new.pkl')
    model_bot = load_trained_model('rf_bot_classifier_new.pkl')
    
    # default predictions from model using threshold = 0.5
    pred_org = model_org.predict(df)
    pred_bot = model_bot.predict(df)
    
    # set threshold cut manually to 0.8 to get FPR = 0.01
    # threshold = 0.88982534 # xgb_model precision = 0.95
    threshold = 0.8
    rf_probs = model_org.predict_proba(df)[:, 1] # column 1 = P(class = 1)
    #pred_org = (rf_probs > threshold).astype(int)
    rf_probs = model_bot.predict_proba(df)[:, 1] # column 1 = P(class = 1)
    #pred_bot = (rf_probs > threshold).astype(int)

    classifications = {'labels_bot':pred_bot, 'labels_org':pred_org}
    df_classify = pd.DataFrame(classifications, columns=['labels_bot','labels_org'])
    df_classify.index = df.index
    #df_classify.to_csv('bot_org_labels.csv')
    
    # show accounts that are both bots and org
    bot = df_classify[df_classify.labels_bot==1]
    print(f'Number of bots: {len(bot)}')
    org = df_classify[df_classify.labels_org==1]
    print(f'Number of orgs: {len(org)}')
    bot_and_org = bot[bot.labels_org==1]
    print(f'Number of bots and orgs: {len(bot_and_org)}')
    