import plotly.graph_objects as go
import numpy as np
import pygrib

grbs = pygrib.open("data/PrecipRate_00.00_20210708-210000.grib2")
grb = grbs[1]

data, lats, lons = grbs[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)

print("Rendering Map.")

fig = go.Figure(data = go.Densitymapbox(
    lat = lats.flatten(),
    lon = lons.flatten(),
    z = data.flatten(),
    radius = 3,
    colorscale= [
        [0, 'rgb(0, 0, 255)'],          #blue
        [1/10_000, 'rgb(0, 128, 128)'], #cyan
        [1/1_000, 'rgb(0, 255, 0)'],    #green
        [1/100, 'rgb(255, 255, 0)'],    #yellow
        [1/10, 'rgb(255, 128, 0)'],     #orange
        [1, 'rgb(255, 0, 0)'],          #red
    ],
))

fig.update_layout(mapbox_style="open-street-map", mapbox_center_lon=180)
fig.show()

print("Done")