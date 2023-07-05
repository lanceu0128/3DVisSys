from multiprocessing import Pool
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
import utilities as util
import pygrib, time, json

start_time = time.time()

heights = ["00.50", "00.75", "01.00", "01.25", "01.50", "01.75", "02.00", "02.25", "02.50", "02.75", "03.00", "03.50", "04.00", "04.50", "05.00", "05.50", "06.00", "06.50", "07.00", "07.50", "08.00", "08.50", "09.00", "10.00", "11.00", "12.00", "13.00", "14.00", "15.00", "16.00", "17.00", "18.00", "19.00"]
file_location = 'data/3Drefl/'
file_time = ""
file_name = 'MRMS_MergedReflectivityQC_'
file_extension = '.grib2'

def process_height_data(height):

    print(f"Processing {height} level data")

    grb = pygrib.open(file_location + file_name + height + file_time + file_extension)
    # data, lats, lons = grb[1].data(lat1=35, lat2=35.5, lon1=-80+360, lon2=-79.5+360) #test for zoomed in area
    data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)

    data[data < 0] = 0
    lons -= 360

    pooled_lats = util.pool_array(lats, 5, 5)
    pooled_lons = util.pool_array(lons, 5, 5)
    pooled_data = util.pool_array(data, 5, 5)
    locations = util.get_locations(pooled_lats, pooled_lons)
    heights = np.full(pooled_data.shape, float(height))

    print(f"{pooled_lats.shape}, {pooled_lons.shape}, {pooled_data.shape}, {locations.shape}, {heights.shape}")

    df_dict = {"lat": pooled_lats.flatten(), "lon": pooled_lons.flatten(), "data": pooled_data.flatten(), "locations": locations.flatten(), "heights": heights.flatten()}
    df = pd.DataFrame(df_dict)

    runtime = time.time() - start_time
    print(f"Finished processing {height} data in {runtime}")

    return df

def grab_data():
    pool = Pool(28)
    height_frames = pool.map(process_height_data, heights) # next get data values at heights

    df = pd.concat(height_frames, ignore_index=True, sort=False)
    print(df.describe())
    print(df.head(10))
    print("Figure Data Grabbed")

    return df

def make_figure(download_time, h, w):
    global file_time
    file_time = download_time

    df = grab_data()
    map_x, map_y, map_z = util.process_map_geojson()

    fig = go.Figure(frames = [go.Frame(data = go.Volume(
        x = df.loc[df['heights'] == height, 'lat'],
        y = df.loc[df['heights'] == height, 'lon'],
        z = df.loc[df['heights'] == height, 'heights'],
        value = df.loc[df['heights'] == height, 'data'],
        isomin = df['data'].min()+0.1,
        isomax = df['data'].max(),
        opacity = 1,
        surface_count = 17,
        ),
        name = str(height)
        )
    for height in df['heights'].unique().tolist()])

    fig.add_trace(go.Volume(
        x = df['lat'],
        y = df['lon'],
        z = df['heights'],
        value = df["data"],
        isomin = 0,
        isomax = 50,
        opacity = 0.2, # best so far: 0.2
        surface_count = 5, #best so far: 5
        colorscale = "Jet",
        # caps = dict(x_show=False, y_show=False, z_show=False),
    ))

    # fig.add_trace(
    #     go.Volume(
    #             x = df.loc[df['heights'] == 0.5, 'lat'],
    #             y = df.loc[df['heights'] == 0.5, 'lon'],
    #             z = df.loc[df['heights'] == 0.5, 'heights'],
    #             value = df.loc[df['heights'] == 0.5, 'data'],
    #             isomin = df['data'].min()+0.1,
    #             isomax = df['data'].max(),
    #             opacityscale = "uniform",
    #             surface_count = 17, # needs to be a large number for good volume rendering
    #         )
    # )

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
                            "label": str(k),
                            "method": "animate",
                        }
                        for k, f in enumerate(fig.frames)
                    ],
                }
            ]

    # Layout
    fig.update_layout(
        height = h,
        width = w,
        scene=dict(
            xaxis_title = "Latitude",
            yaxis_title = "Longitude", 
            zaxis_title = "Height [km; MSL]",
            zaxis=dict(range = [float(df['heights'].min()), float(df['heights'].max())], autorange=False),
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

    fig.show()
    return fig

if __name__ == '__main__':
    make_figure("_2023-07-03_14-42-57", 600, 1000)