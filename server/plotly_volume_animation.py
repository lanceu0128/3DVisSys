from multiprocessing import Pool
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
import utilities as util
import pygrib, time, json, logging

start_time = time.time()

heights = ["00.50", "00.75", "01.00", "01.25", "01.50", "01.75", "02.00", "02.25", "02.50", "02.75", "03.00", "03.50", "04.00", "04.50", "05.00", "05.50", "06.00", "06.50", "07.00", "07.50", "08.00", "08.50", "09.00", "10.00", "11.00", "12.00", "13.00", "14.00", "15.00", "16.00", "17.00", "18.00", "19.00"]
file_location = '/data3/lanceu/server/data/3Drefl/'
# file_location = '/data3/lanceu/server/testdata/SampleData/' #testing only
file_time = ""
file_name = 'MRMS_MergedReflectivityQC_'
file_extension = '.grib2'

logging.basicConfig(level=logging.INFO, filename="/data3/lanceu/server/log.log", filemode="a",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def process_height_data(height):

    logging.debug(f"Processing {height} level data")

    grb = pygrib.open(file_location + file_name + height + file_time + file_extension)
    # data, lats, lons = grb[1].data(lat1=35, lat2=35.5, lon1=-80+360, lon2=-79.5+360) #test for zoomed in area
    data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)

    data[data < 0] = 0
    lons -= 360

    pooled_lats = util.pool_array(lats, 5, 5).flatten()
    pooled_lons = util.pool_array(lons, 5, 5).flatten()
    pooled_data = util.pool_array(data, 5, 5).flatten()
    locations = util.get_locations(pooled_lats, pooled_lons)
    heights = np.full(pooled_data.shape, float(height))

    # logging.info(f"Pooled data shapes: {pooled_lats.shape}, {pooled_lons.shape}, {pooled_data.shape}, {locations.shape}, {heights.shape}")

    df_dict = {"lat": pooled_lats, "lon": pooled_lons, "data": pooled_data, "locations": locations, "heights": heights}
    df = pd.DataFrame(df_dict)

    runtime = time.time() - start_time
    logging.debug(f"Finished processing %s data in %s.", height, str(runtime))

    return df

def grab_data():
    logging.info("Starting volume animation data processing and multithreading.")
    pool = Pool(28)
    height_frames = pool.map(process_height_data, heights) # next get data values at heights

    df = pd.concat(height_frames, ignore_index=True, sort=False)
    logging.info("Finished volume processing data for all heights. Final data:")
    logging.info("\n %s", df.describe())
    return df

def make_figure(download_time, h, w):
    global file_time
    file_time = download_time

    fig = go.Figure()

    df = grab_data()
    elevation_map, _ = util.elevation_map()

    logging.info("Starting Plotly volume animation graph creation.")

    fig.add_trace(
        go.Volume(
            x = df.loc[df['heights'] == 0.5, 'lat'],
            y = df.loc[df['heights'] == 0.5, 'lon'],
            z = df.loc[df['heights'] == 0.5, 'heights'],
            value = df.loc[df['heights'] == 0.5, 'data'],
            isomin = df['data'].min()+0.1,
            isomax = 50,
            opacityscale = "uniform",
            surface_count = 1, # needs to be a large number for good volume rendering,
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
    # Layout
    fig.update_layout(
        title = f"Reflectivity (Animated) {download_time[1:]}",
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

    logging.info("Finished Plotly volume graph creation.")
    return fig

if __name__ == '__main__':
    file_location = '/data3/lanceu/server/testdata/SampleData/' # testing only
    fig = make_figure("_20210708-120040", 600, 1000) # testing only
    fig.show()