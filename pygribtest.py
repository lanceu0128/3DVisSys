import pygrib
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

grbs = pygrib.open("data/MRMS_PrecipRate.latest.grib2")
# grbs = pygrib.open("data/MRMS_PrecipRate_00.00_20230605-165800.grib2")

print(grbs[1].keys())

data, lats, lons = grbs[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)
print(f"{data.shape}, {lats.shape}, {lons.shape}")

lats = lats.flatten()
lons = lons.flatten()

lat = []
lon = []

# grabbing every few value of lats and lons for easier graphing 
for i in range(len(lats)):
    if i % 610 == 0:
        lat.append(lats[i])
        lon.append(lons[i])

fig = px.scatter_geo(lat=lat, lon=lon)
fig.show()