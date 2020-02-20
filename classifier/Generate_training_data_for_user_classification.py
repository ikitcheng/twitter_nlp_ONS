# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 01:46:24 2020

@author: I Kit Cheng
"""

# In[]:

# Generate features from training data
from ScrapeTwitterTimeline_FeatureExtraction import main
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def relabel_dataset(df):
    """

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Dataframe.

    Returns
    -------
    df_labels : pandas.core.frame.DataFrame
        Extracted labels.

    """

    # Label Distribution
    print('\nLabel Distribution:')
    print(df.gender.value_counts())
    
    # Drop rows with gender = nan
    df = df.dropna(subset=['gender'])
    
    # Remove individuals with unknown label
    df = df[df.gender != 'unknown']
    
    print(f'\nClean df length: {len(df)}')
    
    # Label Distribution (clean)
    print('\nLabel Distribution:')
    print(df.gender.value_counts())
    
    # Combine 'male' and 'females' labels to 0, and relabel 'brand' to 1
    df_labels = pd.DataFrame([0 if (x =='female' or x == 'male') 
                              else 1 for x in df.gender], columns=['labels'],
                             index=df.name)
    
    return df_labels

# In[]:


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
    
def matching_labels_to_new_features(df):
    """

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Dataframe without labels.

    Returns
    -------
    df : pandas.core.frame.DataFrame
        Dataframe with labels.

    """
    print('Matching labels to new features dataframe.')
    # Adding the corresponding label to the feature dataset
    labels_for_sample = []
    for i,v in enumerate(df.index.to_list()):
        if len(df_labels.loc[v]) > 1:
            labels_for_sample.append(df_labels.loc[v].iloc[0][0])
        else:
            labels_for_sample.append(df_labels.loc[v].iloc[0])
            
    df.index.names = ['username'] # name the index column
    df['labels'] = labels_for_sample
    df.to_csv('user_features_labels.csv')
    return df


# In[]:

########################################### plot distribution of each variable ######################################
def plotDist(save=False):
    """

    Parameters
    ----------
    save : bool, optional
        Save plot option. The default is False.

    Returns
    -------
    None.

    """
    for i, col in enumerate(df.columns[1:]):
        print(col)
        plt.figure()
        try:
            ax = sns.kdeplot(df[col])
            ax.get_legend().remove()
        except RuntimeError:
            df[col].hist()
        plt.title(col)
        plt.close()
    if save:
        plt.savefig('dist_'+col+'.png')

#plotDist()
# In[]:
######################################### Dealing with missing data ##############################################

from sklearn.impute import SimpleImputer

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
    for i, col in enumerate(df.columns[1:-1]):
        if len(df[col].unique()) == 2: # categorical (binary) data
            continue
        else:
            df[[col]] = imputer.fit_transform(df[[col]])
    return df

# In[]:
if __name__ == '__main__':
    # Set random seed to ensure reproducible runs
    RSEED = 50

    print('\n################# Begin Scraping User Timeline: #####################')
    
    # We'll limit the data to 1000 individuals to speed up training.
    df = pd.read_csv('../Datasets/gender-classifier.csv', encoding = "ISO-8859-1")#.sample(10, random_state = RSEED)
    users = df.name.to_list()
    df_labels = relabel_dataset(df)
    
    scrape = False
    if scrape:
        df = main(users, N=200) # saves features in users_features.csv
    
    df = pd.read_csv('users_features.csv', index_col=0)
    
    df = bool2int(df, ['geo', 'location', 'url', 'description', 'verified'])
    matching_labels_to_new_features(df)
    
    df = pd.read_csv('user_features_labels.csv', index_col=0) # training data (unclean)
    df.index.name = 'username'
    df = replaceNans(df)
    df.to_csv('user_features_labels_noNan.csv')
    print('___________________Done cleaning!_________________')
