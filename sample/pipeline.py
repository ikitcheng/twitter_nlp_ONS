from tools.cleaner import cleaner
from tools.geotagger import geotagger
from tools.wcg import wordcloudgenerator
from tools.classifier import userclassifier
from tools.analyser import sentimentAnalyser
from tools.fex import featureExtractor

import time

def main():

    # ----------------------------------------------
    # Dataset to analyse
    # ----------------------------------------------
    dataset_multiple_csvs = "../Scraper/datasets/Brexit/All_Headers/scrape_data_2020-01-29-2020-01-30.tar.gz"
    dataset_single_csv = ""


    # TODO: test all functions in the cleaner work as expected
    # ----------------------------------------------
    # Clean the data
    # ----------------------------------------------
    cln = cleaner(dataset_multiple_csvs)
    df = cln.read_and_merge_scraped_data()
    df = cln.eliminate_non_ascii_from_json(df, 'entities', 'hashtags')
    print(df['hashtags_list_non_ascii'])
    df = cln.clean_tweet(df)
    print(df['text_cleaned'])
    # etc etc ...


    # TODO: test all functions in the wordcloudgenerator work as expected
    # ----------------------------------------------
    # Generate a Word Cloud for a particular day
    # ----------------------------------------------
    similar_hashtags_dict = "hashtags_for_wordcloudgenerator.json"
    wcg = wordcloudgenerator(df, similar_hashtags_dict)
    wcg.hashtag_freq('hashtags_list_non_ascii')
    print(wcg.hashtags_freq_dict)
    wcg.gen_wordcloud()
    # wcg.gen_word_cloud(wordcloud=False, save=False)



    # ----------------------------------------------
    # Analyse sentiments
    # ----------------------------------------------



    # ----------------------------------------------
    # Feature Extraction
    # ----------------------------------------------
    usernames = df['user.screen_name'].head(3)
    fe = featureExtractor(usernames)
    N = 200
    users_features_df = fe.extract_features(N)
    print(users_features_df)


    # ----------------------------------------------
    # User Classification
    # ----------------------------------------------



    # ----------------------------------------------
    # User Group word clouds
    # ----------------------------------------------



    # ----------------------------------------------
    # Geo Tagging Hashtags & visualising in UI
    # ----------------------------------------------
    gt = geotagger(df)
    save_map_path = "BrexitEvolutionMaps/geotag_2020-01-29-2020-01-30-n=2000.html"
    start = time.time()
    lat_long_df = gt.plot_and_save_map(save_map_path, precise_geo=True)
    print(lat_long_df)
    end = time.time()
    print("Execution time: " + str((end - start)/60) + " mins")



    # TODO: argParser ?