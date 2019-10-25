import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

Chile = gpd.read_file('./Regiones/Regional.shp')

Chile.plot()
plt.show()