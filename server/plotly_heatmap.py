import plotly.graph_objects as go
import numpy as np
import pygrib
import pandas as pd
import utilities as util

coords = {
    "lat1": 37,
    "lat2": 40,
    "lon1": -80,
    "lon2": -75
}
<<<<<<< HEAD:server/plotly_heatmap.py

def grab_data():
    global coords

    grbs = pygrib.open("/home/lanceu/server/data/2Dprecip/MRMS_PrecipRate.grib2")
    grb = grbs[1]

=======

def grab_data():
    global coords

    grbs = pygrib.open("data/2Dprecip/MRMS_PrecipRate.grib2")
    grb = grbs[1]

>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea:app/plotly_heatmap.py
    data, lats, lons = grbs[1].data(lat1=37, lat2=40, lon1= -80 + 360, lon2=-75 + 360)
    lons -= 360

    pooled_lats = util.pool_array(lats, 5, 5)
    pooled_lons = util.pool_array(lons, 5, 5)
    pooled_data = util.pool_array(data, 5, 5)
    locations = util.get_locations(pooled_lats, pooled_lons)

    df_dict = {'lats': pooled_lats.flatten(), 'lons': pooled_lons.flatten(), 'data': pooled_data.flatten(), 'locations': locations.flatten()}
    df = pd.DataFrame(df_dict)
    print(df.head(10))

    return df

def make_figure(download_time, h, w):
    global coords

    df = grab_data()

    fig = go.Figure(data = go.Densitymapbox(
        lat = df['lats'],
        lon =df['lons'],
        z = df['data'],
        customdata = df['locations'],
        radius = 8,
        hovertemplate = """Rain-Rate: %{z} mm/hr <br>Latitude: %{lat} <br>Longitude: %{lon} <br>Location: %{customdata}<extra></extra>""",
        zmax=64,
        # implements log scale
        colorscale= [
            [0, 'rgb(25, 132, 197)'],         
            [1/128-0.001, 'rgb(25, 132, 197)'],          
            [1/128, 'rgb(34, 167, 240)'], 
            [1/64-0.001, 'rgb(34, 167, 240)'], 
            [1/64, 'rgb(99, 191, 240)'],    
            [1/32-0.001, 'rgb(99, 191, 240)'],
            [1/32, 'rgb(167, 213, 237)'],    
            [1/16-0.001, 'rgb(167, 213, 237)'],
            [1/16, 'rgb(225, 166, 146)'],     
            [1/8-0.001, 'rgb(225, 166, 146)'],
            [1/8, 'rgb(222, 110, 86)'],       
            [1/4-0.001, 'rgb(222, 110, 86)'], 
            [1/4, 'rgb(225, 75, 49)'],
            [1/2-0.001, 'rgb(225, 75, 49)'],
            [1/2, 'rgb(194, 55, 40)'],
            [1, 'rgb(194, 55, 40)']
        ],
        colorbar=dict(
<<<<<<< HEAD:server/plotly_heatmap.py
            
            title="Rain-Rate<br>(mm/h)",
=======
            title="mm",
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea:app/plotly_heatmap.py
            thickness=20,
            tickvals=[0.5, 1, 2, 4, 8, 16, 32, 64],
            ticklen=0, 
            tickcolor='black',
            tickfont=dict(size=14, color='black')
            )
        ),
    )

    fig.update_layout(
        title = f"Precipitation {download_time[1:]}",
        mapbox_style="white-bg",
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

    # creates boundary of scrolling; slightly bigger than target region
    fig.update_mapboxes(bounds= dict(
            west = coords["lon1"] - 3,
            east = coords["lon2"] + 3,
            south = coords["lat1"] - 1,
            north = coords["lat2"] + 1,
        )
    )

    # creates boundary box showing region of interest
    fig.add_trace(go.Scattermapbox(
        fill = "none",
        mode = "markers+lines",
        # (lat1, lon1) -> (lat1, lon2) -> (lat2, lon2) -> (lat2, lon1) -> (lat1, lon1)
        lat = [coords["lat1"], coords["lat1"], coords["lat2"], coords["lat2"], coords["lat1"]],
        lon = [coords["lon1"], coords["lon2"], coords["lon2"], coords["lon1"], coords["lon1"]],
        marker = { 'size': 10, 'color': "white" }
        )
    )

    return fig

if __name__ == "__main__":
<<<<<<< HEAD:server/plotly_heatmap.py
    fig = make_figure("test", 650, 1000)
    fig.show()
=======
    make_figure("test", 650, 1000)
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea:app/plotly_heatmap.py
