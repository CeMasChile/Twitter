import geopandas as gpd
import twitterGeoLoc as tgl
import config
from main import get_keywords


Chile = gpd.read_file('./Regiones/Regional.shp')


tgl.read_tweets(config.region, get_keywords())