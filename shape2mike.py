import os
import pandas as pd
import geopandas as gpd
import numpy as np
import sys

infile = sys.argv[0]
outfile = sys.argv[1]

# file = r'C:\Users\cagri\Desktop\shape2mike\Data\Dere.shp'
file = r'C:\Users\cagri\Desktop\shape2mike\Data\Bina.shp'

df = gpd.read_file(file)

type = df.geom_type[0]

g = [i for i in df.geometry]

df_all = pd.DataFrame()
for f in g:
    if type == 'Polygon':
        x = np.array(f.boundary.coords.xy[0])
        y = np.array(f.boundary.coords.xy[1])
    else:
        x = np.array(f.coords.xy[0])
        y = np.array(f.coords.xy[1])
    xy = pd.DataFrame((zip(x,y)))
    xy['cond'] = 1
    xy.iloc[-1, xy.columns.get_loc('cond')] = 0
    df_all = df_all.append(xy)

df_all.to_csv(r'C:\Users\cagri\Desktop\shape2mike\Data\pandas.xyz', header=None, index=None, sep=' ', mode='a')




