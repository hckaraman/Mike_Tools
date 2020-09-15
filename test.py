import os, glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mikeio import Dfs2
from mikeio import Dfsu, Mesh
from mikeio.eum import ItemInfo, EUMType, EUMUnit
from mikeio.dutil import Dataset

dfsu_file = r"C:\Users\cagri\Desktop\Oresund\Calibration_1\Output\flow.dfsu"
dfsu2_file = r"D:\Work_12.02.2017\Q1000_Max.dfs2"
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
k, j = newdfs.find_nearest_element(lon=41.299349, lat=41.348234)
kmax = newds[0].shape[1]
jmax = newds[0].shape[2]

wd = newds["H Water Depth"]
wd_p = wd[:, k, j]
date = newds.time

df = pd.DataFrame({'Date': date, 'WD': wd_p})
df = df.set_index('Date')



newdfs = Dfs2(dfsu2_file)
newds = newdfs.read()
wd = newds['max H']
sp = newds['max Current Speed']

risk = (sp + 0.5) * wd

dx = newdfs._dx
dy = newdfs._dy

x0 = newdfs._longitude
x0 = 440648.320068036
y0 = newdfs._latitude
y0 = 4577194.04335586

nx = newds.data[0].shape[1]
ny = newds.data[0].shape[2]

print(x0, y0, nx, ny, dx, dy)

coordinate = ['ITRF_3_42', x0, y0, -0.468178951376251]

items = [ItemInfo("Mean Sea Level Pressure", EUMType.Air_Pressure, EUMUnit.hectopascal)]
# el = np.expand_dims(risk,axis=0)
d = []
d.append(risk)
dfs = Dfs2()
newdfs.write(filename="risk.dfs2",data=d,coordinate=coordinate, dx=dx, dy=dy,items=[ItemInfo("Elevation", EUMType.Total_Water_Depth)])
newdfs.write(filename="risk.dfs2",data=risk)