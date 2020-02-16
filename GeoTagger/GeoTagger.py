import tarfile
import pandas as pd
import csv
from geopy.geocoders import Nominatim
import geopy


# move this function to the cleaner?
def read_and_merge_scraped_data(dataset, headers):
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
        tar.close()
        return hashtags_df


def get_geo_info(place_name):
    """
    Gets coordinates and address for a given place name using geopy
    """
    # Create geo_locator object instance
    geo_locator = Nominatim(user_agent="myGeocoder")

    # place_name = "Champ de Mars, Paris, France"
    # Attempt to obtain geo data for given place name
    try:
        location = geo_locator.geocode(place_name)
    except Exception:
        return None

    if not location:
        return None

    # return float(location.latitude), float(location.longitude)
    return pd.Series([location.latitude, location.longitude])



# prepare the dataset we wish to analyse
root_dir_data = "../Scraper/datasets/Brexit/All_Headers/"
dataset = root_dir_data + "scrape_data_2020-01-29-2020-01-30.tar.gz"
with open(root_dir_data + "headers.csv", newline='') as f:
    reader = csv.reader(f)
    headers = [row[0] for row in reader]

hashtags_df = read_and_merge_scraped_data(dataset, headers)

print(hashtags_df.head())
print(hashtags_df.shape)

# coords = hashtags_df[hashtags_df['coordinates'].notna()]

# print(coords['coordinates'])
# print(coords.shape)


# place = hashtags_df[hashtags_df['place'].notna()]
# print(place['place'])
# print(place.shape)


# user location is the key value to use!
user_loc = hashtags_df[hashtags_df['user.location'].notna()]
print(user_loc['user.location'])
print(user_loc.shape)


# unique_hashtags = hashtags_df['user.location'].unique()
# print("Number of unique hashtags: ", len(unique_hashtags))
# print(unique_hashtags)

# print(hashtags_df['user.location'])
# unique_locations = hashtags_df['user.location'].unique()
# print("Number of unique locations: ", len(unique_locations))
# print(unique_locations)

# location = get_geo_info(unique_locations[-1])
# print(location)
# print(location.longitude)
# print(location.latitude)

# print(hashtags_df['user.location'].head())
# print(type(hashtags_df['user.location'][0]))


# nominatim_geo_location = [get_geo_info(location) for location in hashtags_df['user.location'].head()]
# print(nominatim_geo_location)


# hashtags_df['nomanatim_geo_location'] = hashtags_df['user.location'].apply(lambda x: get_geo_info(x))
# print(hashtags_df.head())

d = {'user.location': ['Ireland', 'London', 'Manchester', 'Wellingborough']}
df = pd.DataFrame(data=d)
print(df)

df[['geo_lat', 'geo_long']] = df['user.location'].apply(lambda x: get_geo_info(x))
print(df)

# import plotly.express as px
# fig = px.scatter_geo(df, lat=df['geo_lat'], lon=df['geo_long'])
# fig.show()

# TODO: look for 'user.geo_enabled' attribute?? - may be able to extract a non-null lat and long value

import folium

map1 = folium.Map(
    location=[53.8, 4.5],
    tiles='cartodbpositron',
    zoom_start=3,
)
df.apply(lambda row:folium.CircleMarker(location=[row["geo_lat"], row["geo_long"]]).add_to(map1), axis=1)
map1.save('geotagger_test.html')