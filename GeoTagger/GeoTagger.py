import tarfile
import pandas as pd
import csv
from geopy.geocoders import Nominatim
import geopy
import folium
from folium import plugins
from folium.plugins import FastMarkerCluster
import time


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


def get_latitude_longitude(place_name):
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
        # return None
        return pd.Series([None, None])

    if not location:
        # return None
        return pd.Series([None, None])

    # return float(location.latitude), float(location.longitude)
    return pd.Series([location.latitude, location.longitude])


def plot_and_save_map(df, filename):
    """
    Extract coordinates, plot on an interactive map and save to html file
    """
    # # test first N values in scraped data
    N = 1000
    coordinates_df = df.head(N)

    # cocatenate latitude and longitude columns onto df
    coordinates_df[['geo_lat', 'geo_long']] = coordinates_df['user.location'].apply(lambda x: get_latitude_longitude(x))

    # # drop NaNs
    coordinates_df = coordinates_df.dropna(subset=['geo_lat', 'geo_long'], how='all')
    print("Extracted " + str(coordinates_df.shape[0]/N * 100) + " percent of locations")

    map = folium.Map(
        location=[53.8, 4.5],
        tiles='cartodbpositron',
        zoom_start=3,
    )

    # plot and save
    FastMarkerCluster(data=list(zip(coordinates_df['geo_lat'].values, coordinates_df['geo_long'].values))).add_to(map)
    folium.LayerControl().add_to(map)
    map.save(filename)



start = time.time()

# prepare the dataset we wish to analyse
root_dir_data = "../Scraper/datasets/Brexit/All_Headers/"
dataset = root_dir_data + "scrape_data_2020-01-29-2020-01-30.tar.gz"
with open(root_dir_data + "headers.csv", newline='') as f:
    reader = csv.reader(f)
    headers = [row[0] for row in reader]

# process the data
hashtags_df = read_and_merge_scraped_data(dataset, headers)
save_map_path = "BrexitEvolutionMaps/scape_data_test_n=1000.html"
plot_and_save_map(hashtags_df, save_map_path)

end = time.time()
print("Execution time: " + str((end - start)/60) + " mins")

















# TEST WORK

# coords = hashtags_df[hashtags_df['coordinates'].notna()]
# print(coords['coordinates'])
# print(coords.shape)
# place = hashtags_df[hashtags_df['place'].notna()]
# print(place['place'])
# print(place.shape)

# user location is the key value to use!
# user_loc = hashtags_df[hashtags_df['user.location'].notna()]
# print(user_loc['user.location'])
# print(user_loc.shape)

# TODO: look for 'user.geo_enabled' attribute?? - may be able to extract a non-null lat and long value


# -----------------------------------------
# TEST CASE:
# -----------------------------------------
# d = {'user.location': ['Ireland', 'London', 'Manchester', 'Wellingborough', 'sdfshghfhgfvd', 'London']}
# df = pd.DataFrame(data=d)
# print(df)

# df[['geo_lat', 'geo_long']] = df['user.location'].apply(lambda x: get_geo_info(x))
# print(df)

# # drop NaNs
# df = df.dropna(subset=['geo_lat', 'geo_long'], how='all')
# print(df)
# -----------------------------------------



# -----------------------------------------
# TEST CASE:
# -----------------------------------------
# map1 = folium.Map(
#     location=[53.8, 4.5],
#     tiles='cartodbpositron',
#     zoom_start=3,
# )
# df.apply(lambda row:folium.CircleMarker(location=[row["geo_lat"], row["geo_long"]]).add_to(map1), axis=1)

# # add in the quantities of tweets within a certain area
# FastMarkerCluster(data=list(zip(df['geo_lat'].values, df['geo_long'].values))).add_to(map1)
# folium.LayerControl().add_to(map1)

# map1.save('geotagger_test.html')
# -----------------------------------------

