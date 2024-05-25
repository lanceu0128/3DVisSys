from multiprocessing import Pool
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
import utilities as util
import pygrib, time, logging

logging.basicConfig(level=logging.INFO, filename="/data3/lanceu/server/log.log", filemode="a",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def make_figure(download_time, h, w):
    '''
    Automated process for making the 3D volume animation figure. 
    Input: download_time for use in naming, height and width for graph size.
    Output: fig plotly figure object - should be converted to json or html in scripts.py  
    '''
    global file_time
    file_time = download_time

    df = util.grab_data(download_time, "3D reflectivity")
    # gets elevation map from util
    # todo: this elevation map is always the same but is generated again for every graph. 
    #       we could speed up map generation by maybe 5-10 secs each time by reusing a previous version 
    elevation_map, ocean_map = util.elevation_map()

    logging.info("Starting Plotly volume graph creation.")

    volume_plot = go.Volume(
        x = df['lat'],
        y = df['lon'],
        z = df['heights'],
        value = df["data"],
        isomin = 0.1,
        isomax = 50,
        opacity = 0.25, # best so far: 0.2
        surface_count = 5, #best so far: 5
        customdata = df['locations'],
        hovertemplate = "Relectivity: %{value} dBZ <br>Latitude: %{x} <br>Longitude: %{y} <br>Height: %{z} km <br>Location: %{customdata}<extra></extra>",
        colorscale = "jet",
        colorbar = dict(
            title = "dbZ",
            thickness = 20,
            ticklen = 0, 
            tickcolor = 'black',
            tickfont = dict(size=14, color='black')
        )
    )

    fig = go.Figure(data = [volume_plot, elevation_map])

    fig.update_layout(
        title = f"Reflectivity {datetime.strptime(download_time, '_%Y%m%d-%H%M%S').strftime('%B %d, %Y %I:%M:%S %p')}",
        scene=dict(
            xaxis_title = "Latitude",
            yaxis_title = "Longitude", 
            zaxis_title = "Height [km; MSL]",
            aspectmode = 'manual',
            aspectratio = dict(x=1, y=1, z=1), 
            xaxis = dict(range=[37, 40], showgrid=False),
            yaxis = dict(range=[-80, -76], showgrid=False),
            zaxis = dict(range=[0, 15], showgrid=True),
        ),
    )

    fig.update_scenes(yaxis_autorange="reversed")

    logging.info("Finished Plotly volume graph creation.")

    return fig

if __name__ == "__main__":
    file_location = '/data3/lanceu/server/testdata/SampleData/' #testing only
    fig = make_figure("_20210708-120040", 600, 1000) # testing only
    fig.show()