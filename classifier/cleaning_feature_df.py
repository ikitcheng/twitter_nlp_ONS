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
    for i, col in enumerate(df.columns):
        if df[col].values.any() == bool: # categorical (binary) data
            continue
        else:
            df[[col]] = imputer.fit_transform(df[[col]])
    return df

def bool2int(df,columns):
    """

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Dataframe with boolean columns.
    columns : list
        Column names with boolean data.

    Returns
    -------
    df : pandas.core.frame.DataFrame
        Dataframe without boolean data (converted to binary 0 or 1)

    """
    print('\nChanging boolean data to 0 or 1.')
    for col in columns:
        df[col] = df[col].astype(int)
    return df

def main_cleaning(csv_file):
    df = pd.read_csv(csv_file, index_col=0)
    df.index.name = 'username'
    df = bool2int(df, ['geo', 'location', 'url', 'description', 'verified'])
    df = replaceNans(df)
    df.to_csv('user_features_noNan.csv')
    print('___________________Cleaning Complete!_________________')
    return df

if __name__ == '__main__':
    csv_file = '../Datasets/user_classification/ind_vs_bot/brexitday/user_features.csv'
    df = main_cleaning(csv_file)

    

