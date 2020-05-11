# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 13:23:04 2020

@author: Owner
"""
import tarfile
import os
import glob
import pandas as pd
import numpy as np

def read_and_merge_scraped_data(filename):
    """
    Reads data scraped from Twitter & merges all data into a single dataframe
 
    Returns:
    --------
    dataset:      dataframe containing all concatenated csv files
    """
    _, fileExtension = os.path.splitext(filename)
    if fileExtension != '.gz':
        raise TypeError("Data file provided of incorrect type, \n" +
                        "please provide data file of .tar.gz format")
    with tarfile.open(filename, "r") as tar:
        csv_paths = [file for file in tar.getnames() if file.endswith('.csv')]
        dataset = pd.DataFrame()
        for file in csv_paths:
            try:
                # there may be 0 hits for any given search
                current_dataset = pd.read_csv(tar.extractfile(file), 
                                              header=0, 
                                              sep=',', 
                                              low_memory=False)
            except:
                continue
            dataset = pd.concat([dataset, current_dataset])
    
        tar.close()
        df = dataset
        df = df.reset_index(drop=True)
        #df = df.rename({0: 'username', 1: 'labels'}, axis=1)
        return df
    
def drop_duplicates(df):
    return df.drop_duplicates(subset ="username", 
                     keep = 'first', inplace = False)
# In[]:    
if __name__ == '__main__':
    # combine separate hashtag files into daily csv
    files = glob.glob('*.gz')
    for file in files[0:2]:
        dataset = pd.DataFrame()
        print(file)
        df = read_and_merge_scraped_data(file)
        if '2020-01-28' in file:
            current_dataset = df[[6,7,2]]
            current_dataset = current_dataset.rename(
                {2: 'text', 6: 'username', 7: 'location'}, axis=1)
        else:
            current_dataset = df[[7,8,2]]
            current_dataset = current_dataset.rename(
                {2: 'text', 7: 'username', 8: 'location'}, axis=1)
        created_at = file[12:22]    
        current_dataset['created_at'] = [created_at]*len(current_dataset)
        dataset = pd.concat([dataset, current_dataset])
        dataset.to_csv(f'{created_at}_Brexit_username_location_text_time.csv', index=False)
    
# In[]:
    # combine daily csvs into single csv
    file = 'Brexit_username_location_text_time.tar.gz'
    df = read_and_merge_scraped_data(file)
    df.to_csv(f'Brexit_username_location_text_time.csv', index=False)
    df_size = df.shape[0]
# In[]:
    # drop rows with same username
    df_no_dup = drop_duplicates(df)
    df_no_dup.to_csv(f'Brexit_username_location_text_time_no_duplicates.csv',
                     index=False)
    df_no_dup_size = df_no_dup.shape[0]
# In[]:
    # split the (still) massive df into blocks 
    df_blocks = np.array_split(df_no_dup, 10)
    for i, df_block in enumerate(df_blocks):
        df_block.to_csv(f'Brexit_username_location_text_time_{i}.csv',
                     index=False)
    

