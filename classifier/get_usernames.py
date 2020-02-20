# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 15:45:03 2020

@author: I Kit Cheng
"""
# Getting user names from 'All_Headers' csv files 

import pandas as pd

def get_usernames(csv_file):
    """

    Parameters
    ----------
    csv_file : str
        csv filename.

    Returns
    -------
    users : list
        List of usernames.

    """
    df = pd.read_csv(csv_file, header=None)
    users = df[7].to_list()
    return users

if __name__ == '__main__':
    csv_file = 'brexitday.csv'
    users = get_usernames(csv_file)