# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 20:59:17 2020

@author: I Kit Cheng
"""
from sklearn.impute import SimpleImputer
import pandas as pd
import numpy as np

# Replace numerical nans with median (the median is less sensitive to outliers)
def replaceNans(df, strategy='median'):
    """

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A dataframe (rows are examples and columns are features).
    strategy: string, optional
        Replace nans with specified strategy. The default is 'median'. 
        Options are 'mean', 'median', 'most_frequent', 'constant'.

    Returns
    -------
    df : pandas.core.frame.DataFrame
        A dataframe without numerical nans.

    """
    print(f'Replacing Nans with {strategy}.')
    imputer = SimpleImputer(missing_values=np.nan, strategy=strategy)
    for i, col in enumerate(df.columns[2:]):
        if df[col].values.any() == bool: # categorical (binary) data
            continue
        elif df[col].values.any() == str: # text data
            continue
        else:
            df[[col]] = imputer.fit_transform(df[[col]])
    return df

def drop_duplicates(df):
    return df.drop_duplicates(subset ="userid", 
                     keep = 'first', inplace = True)

def remove_userid(df, user_ids):
    """
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A dataframe with 'userid' as one of the columns.
    user_ids : list
        List of user IDs.
        
    Returns
    -------
    df without the specified user_ids

    """
    print('IDs with contradicting labels:')
    for uid in user_ids:
        print(uid)
        df.drop( df[ df.userid == uid ].index , inplace=True)
    return df

def find_contradicting_uids(df):
    """
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A dataframe with 'userid' and 'labels' columns.

    Returns
    -------
    contradicting_ids : list
        A list of user IDs with conflicting labels.

    """
    
    dup_labels = df[df.duplicated(subset='userid', keep=False)].labels.values
    dup_uids = df[df.duplicated(subset='userid', keep=False)].userid.values
    contradicting_ids = []
    
    for i in range(0,len(dup_uids)-1,2):
        if dup_labels[i] == dup_labels[i+1]:
            continue
        else:
            contradicting_ids.append(dup_uids[i])
            
    return contradicting_ids

def main_cleaning(csv_file):
    df_features = pd.read_csv(csv_file, index_col=0)
    df_features = replaceNans(df-features)
    return df_features
    
# In[]:
if __name__ == '__main__':
    features_csv = 'user_features.csv'
    
    df_features = pd.read_csv(features_csv, index_col=0)
    
    # replace nans with median or just drop the rows with nans
    df_features = replaceNans(df-features)
    #df_features = df_features.dropna()
    
    df_labels = pd.read_csv('../../Datasets/user_classification/ind_vs_bot/datasets_all/dataset_human_bot_ground_truth.csv')
    
    # merge features and labels
    df_merge = pd.merge(df_features, df_labels, on='userid')

    # find ids with contradicting labels
    contradicting_ids = find_contradicting_uids(df_merge)
    
    # drop duplicate rows with same id
    drop_duplicates(df_merge)

    # remove the contradicting ids
    remove_userid(df_merge,contradicting_ids)
    
    df_merge = df_merge.drop(columns=['userid'])
    df_merge.to_csv('user_features_labels_noNan.csv', index=False)
