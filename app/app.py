from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pandas as pd
import gzip, shutil, os, json, requests, time
import plotly, pygrib
import plotly_volume

app = Flask(__name__)

def delete_dir(dir):
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

    print(f"Deleted files in directory {dir}")

def get_newest_graph(dir):
    files = os.listdir(dir)
    paths = [os.path.join(dir, file) for file in files]
    return max(paths, key=os.path.getctime)

def download(url, location):
    unzip_location = location.replace(".gz", "").replace(".latest", "")

    r = requests.get(url, allow_redirects=True)
    open(location, 'wb').write(r.content)

    with gzip.open(location, 'rb') as infile:
        with open(unzip_location, 'wb') as outfile:
            shutil.copyfileobj(infile, outfile)

    print(f"Downloading from url {url} into {location}")

    return unzip_location

# checks if there is substantial rain data using smaller 2d file; if True collect 3D data files and create 3D graph
def check_2d():
    url = "https://mrms.ncep.noaa.gov/data/2D/PrecipRate/MRMS_PrecipRate.latest.grib2.gz"
    file_location = "data/2Drefl"
    file = "/MRMS_PrecipRate.latest.grib2.gz"
    location = file_location + file

    unzip_location = download(url, location)

    grb = pygrib.open(unzip_location)
    data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)
    vals_greater_0 = (data > 0).sum()

    # delete_dir(file_location)

    return vals_greater_0

def download_3d():
    print(f"Starting Download.")

    now = datetime.now()
    val_threshold = 0

    if check_2d() <= 0:
        print("Skipping 3D graph creation ")
        return

    file_time = "_" + now.strftime("%Y-%m-%d_%H-%M-%S")
    folder_url = "https://mrms.ncep.noaa.gov/data/3DRefl/MergedReflectivityQC_"
    url_file_name = "/MRMS_MergedReflectivityQC_"
    file_extension = ".latest.grib2.gz"
    file_location = 'data/3Drefl'
    file_name = '/MRMS_MergedReflectivityQC_'
    heights = ["00.50", "00.75", "01.00", "01.25", "01.50", "01.75", "02.00", "02.25", "02.50", "02.75", "03.00", "03.50", "04.00", "04.50", "05.00", "05.50", "06.00", "06.50", "07.00", "07.50", "08.00", "08.50", "09.00", "10.00", "11.00", "12.00", "13.00", "14.00", "15.00", "16.00", "17.00", "18.00", "19.00"]

    for height in heights:
        url = folder_url + height + url_file_name + height + file_extension
        location = file_location + file_name + height + file_time + file_extension

        download(url, location)

    fig = plotly_volume.make_figure(download_time=file_time, h = 650, w = 1000)

    file = "graphs/3Drefl/" + file_time + ".json"
    with open(file, 'w') as f:
        f.write(plotly.io.to_json(fig))

    delete_dir(file_location)

    current_time = datetime.now().time()
    print(f"Finished downloading, processing, and graph creation at {current_time}.")

@app.route('/')
def main(): 

    # download_3d()

    # file = get_newest_graph("graphs/3Drefl")
    # with open(file) as f:
    #     fig = plotly.io.read_json(f)

    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', 
        # graphJSON = graphJSON, 
        title="MRMS Reflectivity Factor", 
        description=f"Source: https://mrms.ncep.noaa.gov/data/3DRefl/"
    )

sched = BackgroundScheduler(daemon = True)
sched.add_job(download_3d, 'interval', minutes=60)
sched.start()