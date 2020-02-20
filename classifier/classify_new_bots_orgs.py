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
    csv_file = '../../Datasets/user_classification/ind_vs_bot/brexitday/user_features.csv'
    df = main_cleaning(csv_file)
    model_org = load_trained_model('rf_smote_org_classifier.pkl')
    model_bot = load_trained_model('rf_smote_bot_classifier.pkl')   
    pred_org = model_org.predict(df)
    pred_bot = model_bot.predict(df)
    classifications = {'labels_bot':pred_bot, 'labels_org':pred_org}
    df_classify = pd.DataFrame(classifications, columns=['labels_bot','labels_org'])
    df_classify.index = df.index
    df_classify.to_csv('bot_org_labels.csv')
    
    # show accounts that are both bots and org
    bot = df_classify[df_classify.labels_bot==1]
    bot_and_org = bot[bot.labels_org==1]
    print(f'Number of bots and orgs: {len(bot_and_org)}')
    