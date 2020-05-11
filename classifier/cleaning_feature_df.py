# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 20:59:17 2020

@author: I Kit Cheng
"""
from sklearn.impute import SimpleImputer
import pandas as pd
import numpy as np
import os
# In[]:

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
        if df[col].values.any() == bool:  # categorical (binary) data
            continue
        elif df[col].values.any() == str:  # text data
            continue
        else:
            df[[col]] = imputer.fit_transform(df[[col]])
    return df


def drop_duplicates(df, subset):
    return df.drop_duplicates(subset=subset,
                              keep='first', inplace=False)


def remove_username(df, usernames):
    """
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A dataframe with 'username' as one of the columns.
    usernames : list
        List of usernames.

    Returns
    -------
    df without the specified usernames.

    """
    print('IDs with contradicting labels:')
    for name in usernames:
        print(name)
        df.drop(df[df.username == name].index, inplace=True)
    return df


def find_contradicting_names(df):
    """
    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A dataframe with 'username' and 'labels' columns.

    Returns
    -------
    contradicting_ids : list
        A list of usernames with conflicting labels.

    """

    dup_labels = df[df.duplicated(subset='username', keep=False)].labels.values
    dup_names = df[df.duplicated(
        subset='username', keep=False)].username.values
    contradicting_names = []

    for i in range(0, len(dup_names) - 1, 2):
        if dup_labels[i] == dup_labels[i + 1]:
            continue
        else:
            contradicting_names.append(dup_names[i])

    return contradicting_names


def main_cleaning(csv_file):
    df_features = pd.read_csv(csv_file, index_col=0)
    df_features = replaceNans(df_features)
    return df_features


# In[]:
if __name__ == '__main__':

    ###########################################
    # CLEANING FEATURE DF FOR GROUND TRUTH DATA
    ###########################################
    features_csv = 'username_features_1_brexitday.csv'

    df_features = pd.read_csv(features_csv)

    # If nan in Tavg type columns- means no such posts found in last 200 posts
    # (infinite time)
    df_features['Tavg_tweet'][df_features['Tavg_reply'].isna()] = 1e10
    df_features['Tavg_ret'][df_features['Tavg_reply'].isna()] = 1e10
    df_features['Tavg_quote'][df_features['Tavg_reply'].isna()] = 1e10
    df_features['Tavg_reply'][df_features['Tavg_reply'].isna()] = 1e10

    # replace nans with median or just drop the rows with nans
    df_features = replaceNans(df_features, strategy='median')
    #df_features = df_features.dropna()

    #df_labels = pd.read_csv('../../Datasets/user_classification/ind_vs_bot/datasets_all/dataset_human_bot_ground_truth.csv')
    df_labels = pd.read_csv(
        '../../Datasets/user_classification/ground_truth/username_labels/ground_truth_username_labels_org2.csv')
    df_labels.labels = df_labels.labels.astype(int)

    # merge features and labels
    df_merge = pd.merge(df_features, df_labels, on='username')

    # find ids with contradicting labels
    contradicting_names = find_contradicting_names(df_merge)

    # drop duplicate rows with same id
    df_merge = drop_duplicates(df_merge, 'userid')

    # remove the contradicting ids
    remove_username(df_merge, contradicting_names)

    df_merge = df_merge.drop(columns=['userid'])
    df_merge.to_csv('user_features_0_noNan.csv', index=False)

# In[]:
    ###########################################
    # CLEANING FEATURE DF FOR UNSEEN DATA
    ###########################################
    folder = 'C:/Users/Owner/OneDrive - University College London/Industry/ONS/Project/Datasets/Brexit/user_features/'
    files = os.listdir(folder)
    features_csv = f'{folder}'
    for file in files:
        print(file)
        df_features = pd.read_csv(f'{folder}{file}')
        df_features['Tavg_tweet'][df_features['Tavg_reply'].isna()] = 1e10
        df_features['Tavg_ret'][df_features['Tavg_reply'].isna()] = 1e10
        df_features['Tavg_quote'][df_features['Tavg_reply'].isna()] = 1e10
        df_features['Tavg_reply'][df_features['Tavg_reply'].isna()] = 1e10
        df_features = replaceNans(df_features, strategy='median')
        df_features = df_features.drop(columns=['userid'])
        df_features.to_csv(f'{file[:-4]}_noNan.csv', index=False)
