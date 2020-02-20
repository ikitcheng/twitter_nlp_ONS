# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 17:05:55 2020

@author: I Kit Cheng
"""

import json

def parse_json(filename):
    """

    Parameters
    ----------
    filename : string
        Full path to the json file.

    Returns
    -------
    data : dict or list
        Returns a dictionary or a list of dictionaries.

    """
    
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

# In[]:    
if __name__ == "__main__":
    filename = '../Datasets/user_classification/ind_vs_org/organization_training_unbalanced_lower.json'
    data = parse_json(filename)
    
    usernames_labels = []
    for i, uid in enumerate(data['users'].keys()):
        user_data = data['users'][uid]
        usernames_labels.append([user_data['username'],user_data['label']])
