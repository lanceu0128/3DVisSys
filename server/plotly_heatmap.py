import plotly.graph_objects as go
import numpy as np
import pygrib, logging
import pandas as pd
import utilities as util
from datetime import datetime

# map boundaries for all maps
coords = {
    "lat1": 37,
    "lat2": 40,
    "lon1": -80,
    "lon2": -75
}

# server logging for
logging.basicConfig(level=logging.INFO, filename="/data3/lanceu/server/log.log", filemode="a",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def grab_data():
    '''
    Processes 2D precipitation map data from pygrib file and outputs a datafrmae. 
    '''
    global coords

    logging.info(f"Starting heatmap data processing.")

    grbs = pygrib.open("/data3/lanceu/server/data/2Dprecip/MRMS_PrecipRate.grib2")
    grb = grbs[1]

    data, lats, lons = grbs[1].data(lat1=37, lat2=40, lon1= -80 + 360, lon2=-75 + 360)
    lons -= 360 # +- 360 needed for weird grib file format from MRMS

    # pool arrays to reduce size - might not be needed to this degree for 2D heatmaps though? 
    # flatten arrays for easy dataframe usage
    pooled_lats = util.pool_array(lats, 5, 5).flatten()
    pooled_lons = util.pool_array(lons, 5, 5).flatten()
    pooled_data = util.pool_array(data, 5, 5).flatten()
    # get locations for our coordinates from stored API output
    locations = util.get_locations(pooled_lats, pooled_lons)

    df_dict = {'lats': pooled_lats, 'lons': pooled_lons, 'data': pooled_data, 'locations': locations}
    df = pd.DataFrame(df_dict)

    logging.info(f"Finished heatmap data processing. Final data:")
    logging.info("\n %s", df.describe())

    return df

def make_figure(download_time, h, w):
    '''
    Automated process for making the 2D heatmap figure. 
    Input: download_time for use in naming, height and width for graph size.
    Output: fig plotly figure object - should be converted to json or html in scripts.py  
    '''
    global coords

    df = grab_data()

    logging.info("Starting Plotly heatmap graph creation.")

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
            [0, 'rgb(0, 127, 255)'],         
            [1/128-0.001, 'rgb(0, 127, 255)'],          
            [1/128, 'rgb(0, 255, 255)'], 
            [1/64-0.001, 'rgb(0, 255, 255)'], 
            [1/64, 'rgb(0, 255, 127)'],    
            [1/32-0.001, 'rgb(0, 255, 127)'],
            [1/32, 'rgb(0, 255, 0)'],    
            [1/16-0.001, 'rgb(0, 255, 0)'],
            [1/16, 'rgb(127, 255, 0)'],     
            [1/8-0.001, 'rgb(127, 255, 0)'],
            [1/8, 'rgb(255, 255, 0)'],       
            [1/4-0.001, 'rgb(255, 255, 0)'], 
            [1/4, 'rgb(255, 127, 0)'],
            [1/2-0.001, 'rgb(255, 127, 0)'],
            [1/2, 'rgb(255, 0, 0)'],
            [1, 'rgb(255, 0, 0)']
        ],
        colorbar=dict(
            
            title="Rain-Rate<br>(mm/h)",
            thickness=20,
            tickvals=[0.5, 1, 2, 4, 8, 16, 32, 64],
            ticklen=0, 
            tickcolor='black',
            tickfont=dict(size=14, color='black')
            )
        ),
    )

    fig.update_layout(
        title = f"Precipitation {datetime.strptime(download_time, "_%Y%m%d-%H%M%S").strftime("%B %d, %Y %I:%M:%S %p")}",
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

    logging.info("Finished Plotly heatmap graph creation.")

    return fig

if __name__ == "__main__":
    fig = make_figure("test", 650, 1000)
    fig.show()