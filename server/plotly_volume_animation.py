from multiprocessing import Pool
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
import utilities as util
import pygrib, time, json, logging

logging.basicConfig(level=logging.INFO, filename="/data3/lanceu/server/log.log", filemode="a",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def make_figure(download_time, h, w):
    '''
    Automated process for making the 3D volume animation figure. 
    Input: download_time for use in naming, height and width for graph size.
    Output: fig plotly figure object - should be converted to json or html in scripts.py  
    '''

    fig = go.Figure()

    df = util.grab_data(download_time, "3D animation")
    # todo: this elevation map is always the same but is generated again for every graph. 
    #       we could speed up map generation by maybe 5-10 secs each time by reusing a previous version 
    elevation_map, _ = util.elevation_map()

    logging.info("Starting Plotly volume animation graph creation.")

    # each trace = a height level/animation in the map. we add 0.5 twice since it's the default 
    fig.add_trace(
        go.Volume(
            x = df.loc[df['heights'] == 0.5, 'lat'],
            y = df.loc[df['heights'] == 0.5, 'lon'],
            z = df.loc[df['heights'] == 0.5, 'heights'],
            value = df.loc[df['heights'] == 0.5, 'data'],
            isomin = df['data'].min()+0.1,
            isomax = 50,
            opacityscale = "uniform",
            surface_count = 1,
            colorscale= "jet",
            colorbar=dict(
                title="dbZ",
                thickness=20,
                ticklen=0, 
                tickcolor='black',
                tickfont=dict(size=14, color='black')
            )
        )
    )

    # list comprehension for making a frame for every height level
    frames = [
    go.Frame(data=[go.Volume(
            x=df.loc[df['heights'] == height, 'lat'],
            y=df.loc[df['heights'] == height, 'lon'],
            z=df.loc[df['heights'] == height, 'heights'],
            value=df.loc[df['heights'] == height, 'data'],
            isomin=0.1,
            isomax=df['data'].max(),
            opacity=1,
            surface_count=1,
            customdata=df['locations'],
            hovertemplate="""Relectivity: %{value} dBZ <br>Latitude: %{x} <br>Longitude: %{y} <br>Height: %{z} km <br>Location: %{customdata} <extra></extra>""",
            colorscale="jet",
            colorbar=dict(
                title="dbZ",
                thickness=20,
                ticklen=0,
                tickcolor='black',
                tickfont=dict(size=14, color='black')
            )
        )],
            name=str(height)
        )
        for height in df['heights'].unique().tolist()
    ]

    fig.frames = frames
    fig.add_trace(elevation_map)

    # configuration for the slider. 
    # sourced almost entirely from: https://plotly.com/python/visualizing-mri-volume-slices/
    def frame_args(duration):
        return {
            "frame": {"duration": duration},
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},
        }

    sliders = [
        {
            "pad": {"b": 10, "t": 60},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                {
                    "args": [[f.name], frame_args(0)],
                    "label": f.name,
                    "method": "animate",
                }
                for k, f in enumerate(fig.frames)
            ],
        }
    ]

    # Layout configuration
    fig.update_layout(
        title = f"Reflectivity {datetime.strptime(download_time, '_%Y%m%d-%H%M%S').strftime('%B %d, %Y %I:%M:%S %p')}",
        scene=dict(
            xaxis_title = "Latitude",
            yaxis_title = "Longitude", 
            zaxis_title = "Height [km; MSL]",
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1), 
            xaxis=dict(
                range=[37, 40],  # Set the range for the y-axis
                autorange=False  # Disable autorange for the y-axis
            ),
            yaxis=dict(
                range=[-80, -75],  # Set the range for the y-axis
                autorange=False  # Disable autorange for the y-axis
            ),
            zaxis=dict(
                range=[0, 19],  # Set the range for the y-axis
                autorange=False  # Disable autorange for the y-axis
            )
        ),
        updatemenus = [
            {
                "buttons": [
                    {
                        "args": [None, frame_args(50)],
                        "label": "&#9654;", # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;", # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
        ],
        sliders=sliders
    )

    fig.update_scenes(yaxis_autorange="reversed")

    logging.info("Finished Plotly volume animation graph creation.")

    return fig

if __name__ == '__main__':
    file_location = '/data3/lanceu/server/testdata/SampleData/' # testing only
    fig = make_figure("_20210708-120040", 600, 1000) # testing only
    fig.show()