# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 21:32:26 2020

@author: I Kit Cheng
"""
from cleaning_feature_df import replaceNans, drop_duplicates
import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def load_trained_model(model_pkl_file):
    return pickle.load(open(model_pkl_file, "rb"))


def plot_label_distribution(labels):
    plt.figure()
    sns.countplot(x=labels, color='black')
    plt.title('Class distribution', fontsize=16)
    plt.ylabel('Class Counts', fontsize=16)
    plt.xlabel('Class Label', fontsize=16)
    plt.xticks(rotation='vertical')
    for p in plt.gca().patches:
        plt.gca().annotate('{:.0f}'.format(p.get_height()),
                           (p.get_x() + 0.25, p.get_height() + 50))
    plt.tight_layout()

# In[]:


if __name__ == '__main__':
    # load username_features file into dataframe
    csv_file = '../../Datasets/Brexit/user_features/Brexit/username_features_noNan_combined/Brexit_username_features_noNan_combined.csv'
    csv_file = 'username_features_bots_test.csv'
    df = pd.read_csv(csv_file)
# In[]:
    # cleaning
    # If nan in Tavg type columns- means no such posts found in last 200 posts
    # (infinite time)
    df['Tavg_tweet'][df['Tavg_reply'].isna()] = 1e10
    df['Tavg_ret'][df['Tavg_reply'].isna()] = 1e10
    df['Tavg_quote'][df['Tavg_reply'].isna()] = 1e10
    df['Tavg_reply'][df['Tavg_reply'].isna()] = 1e10
    df = replaceNans(df, strategy='median')

# In[]:
    # drop any duplicates based on username column
    if 'userid' in df.columns:
        df = df.drop(columns=['userid'])
    df_no_dup = drop_duplicates(df, col='username')
    df_no_dup.index = df_no_dup.pop('username')

# In[]:
    # load models
    #model_org = load_trained_model('rf_org_classifier_new.pkl')
    #model_bot = load_trained_model('rf_bot_classifier_new.pkl')
    model = load_trained_model(
        'fine_tunned_models/xgb_classifier_human_bot_org_colab.pkl')

 # In[]:
    # default predictions from model using threshold = 0.5
    #pred_org = model_org.predict(df)
    #pred_bot = model_bot.predict(df)
    pred = model.predict(df_no_dup)

# In[]:
    ############### For binary classification only ##############
    # set threshold cut manually to 0.8 to get FPR = 0.01
    # threshold = 0.88982534 # xgb_model precision = 0.95
    threshold = 0.8
    rf_probs = model_org.predict_proba(df)[:, 1]  # column 1 = P(class = 1)
    #pred_org = (rf_probs > threshold).astype(int)
    rf_probs = model_bot.predict_proba(df)[:, 1]  # column 1 = P(class = 1)
    #pred_bot = (rf_probs > threshold).astype(int)

# In[]:
    # put the classifications into a new dataframe: username, labels

    # two binary classifications: human vs bot, human vs organisation
    classifications = {'labels_bot': pred_bot, 'labels_org': pred_org}
    df_classify = pd.DataFrame(
        classifications, columns=[
            'labels_bot', 'labels_org'])
    df_classify.index = df_no_dup.index
    # df_classify.to_csv('bot_org_labels.csv')

    # single multiclass classification: human vs bot vs organisations
    classifications = {'labels': pred}
    df_classify = pd.DataFrame(classifications, columns=['labels'])
    df_classify.index = df_no_dup.index
    df_classify.to_csv('Covid_username_labels.csv')

# In[]:
    # show accounts that are humans, bots or org
    human = df_classify[df_classify.labels == 0]
    print(f'Number of humans: {len(human)}')
    bot = df_classify[df_classify.labels == 1]
    print(f'Number of bots: {len(bot)}')
    org = df_classify[df_classify.labels == 2]
    print(f'Number of orgs: {len(org)}')

    plot_label_distribution(df_classify.labels)
    # bot_and_org = bot[bot.labels_org==1]
    # print(f'Number of bots and orgs: {len(bot_and_org)}')

# In[]:
    # add location detail into the username labels file
    from read_tar import read_and_merge_scraped_data
    csv_file_labels = '../../Datasets/Brexit/user_labels/Brexit_username_labels.csv'
    file_with_brexit_location = '../../Datasets/Brexit/scrape_data/Brexit_username_location_text_time_combined.tar.gz'
    file_with_brexitday_location = '../../Datasets/Brexit/scrape_data/brexitday/Brexitday_username_location_text_time_combined.tar.gz'

    df_labels = pd.read_csv(csv_file_labels)

    df_loc_brexit = read_and_merge_scraped_data(file_with_brexit_location)
    df_loc_brexitday = read_and_merge_scraped_data(
        file_with_brexitday_location)
    df_loc_Brexit_all = pd.concat(
        [df_loc_brexit, df_loc_brexitday], ignore_index=True)

    df_merge = pd.merge(df_labels, df_loc_brexit, on='username')

# In[]:

    # Looking at the feature distribution of the scraped data
    # Brexit
    csv_file = 'C:/Users/Owner/OneDrive - University College London/Industry/ONS/Project/Datasets/scraped_data/Brexit/user_features/Brexit/username_features_noNan_combined/Brexit_username_features_noNan_combined.csv'
    df = pd.read_csv(csv_file)

    # age
    sns.distplot(df.age / (365 * 24 * 3600))

    # Covid
    csv_file = 'C:/Users/Owner/OneDrive - University College London/Industry/ONS/Project/Datasets/scraped_data/Covid/Covid_username_features_noNan_combined.csv'
    df = pd.read_csv(csv_file)

    # age
    sns.distplot(df.age / (365 * 24 * 3600))
