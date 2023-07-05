import numpy as np
import pygrib
import pandas as pd
import time
import json
from multiprocessing import Pool
import plotly.graph_objects as go

start_time = time.time()
np.set_printoptions(threshold=np.inf)

heights = ["00.50", "00.75", "01.00", "01.25", "01.50", "01.75", "02.00", "02.25", "02.50", "02.75", "03.00", "03.50", "04.00", "04.50", "05.00", "05.50", "06.00", "06.50", "07.00", "07.50", "08.00", "08.50", "09.00", "10.00", "11.00", "12.00", "13.00", "14.00", "15.00", "16.00", "17.00", "18.00", "19.00"]
file_location = 'app/data/3Drefl/MergedReflectivityQC_'
downloadTime = ".2023_06_21-13-42-57"
file_extension = downloadTime +'.latest.grib2'

def process_height_data(height):
    print(f"Processing {height} level data")

    grb = pygrib.open(file_location + height + file_extension)
    data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)

    data[data < 0] = 0
    
    # Reshape the arrays into a (60x100x5x5) shape
    lon_patch = lons.reshape(60, 5, 100, 5)
    lat_patch = lats.reshape(60, 5, 100, 5)
    data_patch = data.reshape(60, 5, 100, 5)

    # Compute the mean of each 5x5 patch
    lon_mean = np.mean(lon_patch, axis=(1, 3))
    lat_mean = np.mean(lat_patch, axis=(1, 3))
    data_mean = np.mean(data_patch, axis=(1, 3))
    heights = np.full((60,100), float(height))

    print(f"{lon_mean.shape}, {lat_mean.shape}, {data_mean.shape}, {heights.shape}")

    df_dict = {"lat": lat_mean.flatten(), "lon": lon_mean.flatten(), "data": data_mean.flatten(), "heights": heights.flatten()}
    df = pd.DataFrame(df_dict)

    runtime = time.time() - start_time
    print(f"Finished processing {height} data in {runtime}")

    return df

def grab_data(downloadTime):
    pool = Pool(28)

    height_frames = pool.map(process_height_data, heights)

    df = pd.concat(height_frames, ignore_index=True, sort=False)
    print(df.describe())
    print(df.head(10))
    print("Figure Data Grabbed")

    return df

def make_figure(downloadTime, h, w):
    df = grab_data(downloadTime)

    fig = go.Figure(frames = [go.Frame(data = go.Volume(
        x = df.loc[df['heights'] == height, 'lat'],
        y = df.loc[df['heights'] == height, 'lon'],
        z = df.loc[df['heights'] == height, 'heights'],
        value = df.loc[df['heights'] == height, 'data'],
        isomin = df['data'].min()+0.1,
        isomax = df['data'].max(),
        opacityscale = "uniform",
            surface_count = 17, # needs to be a large number for good volume rendering
        ),
        name = str(height)
        )
    for height in df['heights'].unique().tolist()])

    fig.add_trace(
        go.Volume(
                x = df.loc[df['heights'] == 0.5, 'lat'],
                y = df.loc[df['heights'] == 0.5, 'lon'],
                z = df.loc[df['heights'] == 0.5, 'heights'],
                value = df.loc[df['heights'] == 0.5, 'data'],
                isomin = df['data'].min()+0.1,
                isomax = df['data'].max(),
                opacityscale = "uniform",
                surface_count = 17, # needs to be a large number for good volume rendering
            )
    )

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

    with open(file, 'w') as f:
        f.write(pio.to_json(fig))

if __name__ == '__main__':
    make_figure(".2023_06_21-13-42-57", 600, 1000)