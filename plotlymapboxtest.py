import plotly.graph_objects as go
import numpy as np
import pygrib

grbs = pygrib.open("data/PrecipRate_00.00_20210708-210000.grib2")
grb = grbs[1]

coords = {
    "lat1": 37,
    "lat2": 40,
    "lon1": -80,
    "lon2": -75
}

data, lats, lons = grbs[1].data(lat1=coords['lat1'], lat2=coords['lat2'], lon1= coords["lon1"] + 360, lon2= coords["lon2"] + 360)

print("Rendering Map.")

fig = go.Figure(data = go.Densitymapbox(
    lat = lats.flatten(),
    lon = lons.flatten(),
    z = data.flatten(),
    radius = 3,
    hovertemplate = "Precipitation: %{z} <br>(%{lat:.2f}, %{lon:.2f})<extra></extra>",
    showlegend = False,
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