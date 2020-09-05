import os, glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mikeio import Dfs2
from mikeio import Dfsu, Mesh


dfsu_file = r"C:\Users\cagri\Desktop\Oresund\Calibration_1\Output\flow.dfsu"
dfsu2_file = r"D:\Work_12.02.2017\Q1000.dfs2"
m_file = r"C:\Users\cagri\Desktop\Oresund\Data\1993\Bathymetry\oresund.mesh"

# Read mesh file

msh = Mesh(m_file)
msh.plot()
plt.show()

# Read dfsu file

tt = Dfsu(dfsu_file)
ds = tt.read('Surface elevation')
idx = tt.find_nearest_element(349875.801202, 6151146.404113)
selds = ds.isel(idx=idx)
selds



# Read dfsu2 file
newdfs = Dfs2(dfsu2_file)
newds = newdfs.read()
# wd = newds.read("H Water Depth")
k,j = newdfs.find_nearest_element(lon= 41.299349,lat= 41.348234)
kmax = newds[0].shape[1]
jmax = newds[0].shape[2]

wd = newds["H Water Depth"]
wd_p = wd[:,k,j]
date = newds.time

df = pd.DataFrame({'Date':date, 'WD':wd_p})
df = df.set_index('Date')