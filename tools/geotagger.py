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

class geotagger:

    def __init__(self, df):
        """
        cleaned df!!
        """
        self.df = df



    def plot_and_save_map(self, filename, precise_geo=False):
        """
        Extract coordinates, plot on an interactive map and save to html file
        """
        # TODO: remove these 2 lines, here for testing purposes
        # test first N values in scraped data
        N = 2000
        lat_long_df = self.df.head(N)

        #lat_long_df = self.df

        # concatenate latitude and longitude columns onto df
        lat_long_df[['geo_lat', 'geo_long']] = lat_long_df['user.location'].apply(lambda x: self.__get_latitude_longitude(x))
        # # drop NaNs
        lat_long_df = lat_long_df.dropna(subset=['geo_lat', 'geo_long'], how='all')

        precise_geo_df = pd.DataFrame()
        precise_coords_df = pd.DataFrame(columns=['user.location', 'geo_lat', 'geo_long'])
        if precise_geo:
            # geo enabled place & coords
            precise_geo_series = self.df['place'].dropna()
            precise_coords_series = self.df['coordinates'].dropna()

            precise_geo_df = pd.DataFrame({'place' : precise_geo_series})
            precise_geo_df[['geo_lat', 'geo_long']] = precise_geo_df['place'].apply(lambda x: self.__get_latitude_longitude(x))
            precise_geo_df = precise_geo_df.dropna(subset=['geo_lat', 'geo_long'], how='all')
            precise_geo_df.rename(columns={"place": "user.location"})

            precise_coords_df = pd.DataFrame({'place' : precise_coords_series})
            precise_coords_df[['geo_lat', 'geo_long']] = precise_coords_df['place'].apply(lambda x: self.__get_precise_coords(x))
        
        lat_long_df = pd.concat([lat_long_df, precise_geo_df, precise_coords_df])
        
        # TODO: remove these 2 lines, here for testing purposes
        print(lat_long_df.shape)
        print("Extracted " + str(lat_long_df.shape[0]/N * 100) + " percent of locations")

        map = folium.Map(
            location=[53.8, 4.5],
            tiles='cartodbpositron',
            zoom_start=3,
        )

        # plot and save
        FastMarkerCluster(data=list(zip(lat_long_df['geo_lat'].values, lat_long_df['geo_long'].values))).add_to(map)
        folium.LayerControl().add_to(map)
        map.save(filename)

        return lat_long_df



    def __get_latitude_longitude(self, place_name):
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
            return pd.Series([None, None])

        if not location:
            return pd.Series([None, None])

        return pd.Series([location.latitude, location.longitude])


    def __get_precise_coords(self, precise_coords_series):
        long_lat = ast.literal_eval(precise_coords_series).get('coordinates')
        return pd.Series([long_lat[1], long_lat[0]])

