import geopandas as gpd

import config
import twitterGeoLoc as tgl
from main import get_keywords

Chile = gpd.read_file('./Regiones/Regional.shp')


tgl.read_tweets(config.region, get_keywords())