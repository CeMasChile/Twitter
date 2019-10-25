import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import plotly.offline as plty
import process_tweets as pt
import twitterGeoLoc as tgl
import config
from main import get_keywords


Chile = gpd.read_file('./Regiones/Regional.shp')


tgl.read_tweets(config.region, get_keywords())