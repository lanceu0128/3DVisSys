import plotly.graph_objects as go
import numpy as np
import pygrib
import pandas as pd
import utilities as util

grbs = pygrib.open("data/2Drefl/MRMS_PrecipRate.grib2")
grb = grbs[1]

coords = {
    "lat1": 37,
    "lat2": 40,
    "lon1": -80,
    "lon2": -75
}

data, lats, lons = grbs[1].data(lat1=37, lat2=40, lon1= -80 + 360, lon2=-75 + 360)

lons -= 360

pooled_lats = util.pool_array(lats, 5, 5)
pooled_lats = np.around(pooled_lats, decimals = 3)
pooled_lons = util.pool_array(lons, 5, 5)
pooled_lons = np.around(pooled_lons, decimals = 3)
pooled_data = util.pool_array(data, 5, 5)
locations = util.get_locations(pooled_lats, pooled_lons)

df_dict = {'lats': pooled_lats.flatten(), 'lons': pooled_lons.flatten(), 'data': pooled_data.flatten(), 'locations': locations.flatten()}
df = pd.DataFrame(df_dict)
print(df.head(10))

fig = go.Figure(data = go.Densitymapbox(
    lat = df['lats'],
    lon =df['lons'],
    z = df['data'],
    customdata = df['locations'],
    radius = 8,
    hovertemplate = """Reflectivity: %{z} dBZ <br>Latitude: %{lat:.2f} <br>Longitude: %{lon:.2f} <br>Location: %{customdata}<extra></extra>""",
    # showlegend = False,
    colorscale= [
        [0, 'rgb(0, 0, 255)'],          #blue
        [1/10_000, 'rgb(0, 128, 128)'], #cyan
        [1/1_000, 'rgb(0, 255, 0)'],    #green
        [1/100, 'rgb(255, 255, 0)'],    #yellow
        [1/10, 'rgb(255, 128, 0)'],     #orange
        [1, 'rgb(255, 0, 0)'],          #red
    ],
    colorbar=dict(
        thickness=20,
        ticklen=0, 
        tickcolor='black',
        tickfont=dict(size=14, color='black')
        )
    ),
)

fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
    ],
)

fig.update_mapboxes(bounds= dict(
    west = coords["lon1"] - 5,
    east = coords["lon2"] + 5,
    south = coords["lat1"] - 1,
    north = coords["lat2"] + 1,
    )
)

fig.add_trace(go.Scattermapbox(
    fill = "none",
    mode = "markers+lines",
    # (lat1, lon1) -> (lat1, lon2) -> (lat2, lon2) -> (lat2, lon1) -> (lat1, lon1)
    lat = [coords["lat1"], coords["lat1"], coords["lat2"], coords["lat2"], coords["lat1"]],
    lon = [coords["lon1"], coords["lon2"], coords["lon2"], coords["lon1"], coords["lon1"]],
    marker = { 'size': 10, 'color': "white" }
    )
)

fig.show()

print("Done")