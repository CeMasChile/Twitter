import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

Chile = gpd.read_file('./Comunas/comunas.shp')

Chile.plot()
plt.show()