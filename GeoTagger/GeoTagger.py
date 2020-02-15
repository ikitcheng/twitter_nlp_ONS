import tarfile
import pandas as pd
import csv


# move this function to the cleaner?
def read_and_merge_single_day_scraped_data(dataset, headers):
    """
    Reads data scraped from Twitter & merges all data into a single dataframe

    Params:
    -------
    str(dataset):    path to tar.gz dataset file containing multiple csv files
    str(headers):    path to csv file containing column names of dataframe

    Returns:
    --------
    hashtags_df:     dataframe containing all concatenated csv files
    """
    with tarfile.open(dataset, "r:*") as tar:
        csv_paths = [file for file in tar.getnames() if file.endswith('.csv')]
        hashtags_df = pd.DataFrame()
        for file in csv_paths:
            try:
                # there may be 0 hits for any given search
                current_hashtag = pd.read_csv(tar.extractfile(file), header=None, sep=',', low_memory=False)
            except:
                continue
            hashtags_df = pd.concat([hashtags_df, current_hashtag])
        
        hashtags_df.columns = headers
        return hashtags_df


# prepare the dataset we wish to analyse
root_dir_data = "../Scraper/datasets/Brexit/All_Headers/"
dataset = root_dir_data + "scrape_data_2020-01-29-2020-01-30.tar.gz"
with open(root_dir_data + "headers.csv", newline='') as f:
    reader = csv.reader(f)
    headers = [row[0] for row in reader]

hashtags_df = read_and_merge_single_day_scraped_data(dataset, headers)

print(hashtags_df.head())
print(hashtags_df.shape)
print(hashtags_df['user.location'])