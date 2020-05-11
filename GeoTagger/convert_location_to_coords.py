import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import geopy
import folium
import re
import ast
from argparse import ArgumentParser
import time

parser = ArgumentParser(
        description="Scrape twitter API for a hashtag")
parser.add_argument(
        '--filename',
	'-f',
        help="file paht")


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

def convert_to_string(x):
    return str(x)



args = parser.parse_args()
filename = args.filename

df = pd.read_csv(filename)
df[['geo_lat', 'geo_long']] = df['location'].apply(lambda x: get_latitude_longitude(x))

print(df)
df.to_csv(filename, index=False)

