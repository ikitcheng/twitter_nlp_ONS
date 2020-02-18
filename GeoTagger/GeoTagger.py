import tarfile
import pandas as pd
import csv
from geopy.geocoders import Nominatim
import geopy
import folium
from folium import plugins
from folium.plugins import FastMarkerCluster
import time
import re
import ast


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


def get_precise_coords(precise_coords_series):
    long_lat = ast.literal_eval(precise_coords_series).get('coordinates')
    return pd.Series([long_lat[1], long_lat[0]])


def plot_and_save_map(df, filename, precise_geo=True):
    """
    Extract coordinates, plot on an interactive map and save to html file
    """
    # TODO: the next 2 lines will eventually be deleted - here for testing purposes
    # test first N values in scraped data
    N = 100
    lat_long_df = df.head(N)

    # cocatenate latitude and longitude columns onto df
    lat_long_df[['geo_lat', 'geo_long']] = lat_long_df['user.location'].apply(lambda x: get_latitude_longitude(x))
    # # drop NaNs
    lat_long_df = lat_long_df.dropna(subset=['geo_lat', 'geo_long'], how='all')
    print("Extracted " + str(lat_long_df.shape[0]/N * 100) + " percent of locations")

    precise_geo_df = pd.DataFrame()
    precise_coords_df = pd.DataFrame(columns=['user.location', 'geo_lat', 'geo_long'])
    if precise_geo:
        # geo enabled place & coords
        precise_geo_series = hashtags_df['place'].dropna()
        precise_coords_series = hashtags_df['coordinates'].dropna()

        precise_geo_df = pd.DataFrame({'place' : precise_geo_series})
        precise_geo_df[['geo_lat', 'geo_long']] = precise_geo_df['place'].apply(lambda x: get_latitude_longitude(x))
        precise_geo_df = precise_geo_df.dropna(subset=['geo_lat', 'geo_long'], how='all')
        precise_geo_df.rename(columns={"place": "user.location"})

        precise_coords_df = pd.DataFrame({'place' : precise_coords_series})
        precise_coords_df[['geo_lat', 'geo_long']] = precise_coords_df['place'].apply(lambda x: get_precise_coords(x))
    
    lat_long_df = pd.concat([lat_long_df, precise_geo_df, precise_coords_df])
    print(lat_long_df.shape)

    map = folium.Map(
        location=[53.8, 4.5],
        tiles='cartodbpositron',
        zoom_start=3,
    )

    # plot and save
    FastMarkerCluster(data=list(zip(lat_long_df['geo_lat'].values, lat_long_df['geo_long'].values))).add_to(map)
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
save_map_path = "BrexitEvolutionMaps/scape_data_test_with_precise_geo_n=2000.html"
# save_map_path = "BrexitEvolutionMaps/scape_data_test_with_precise_geo_n=10.html"
plot_and_save_map(hashtags_df, save_map_path)

end = time.time()
print("Execution time: " + str((end - start)/60) + " mins")