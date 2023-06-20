from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import gzip, shutil
import time, datetime
import plotly_animated_volume
import json
import plotly
from datetime import datetime

app = Flask(__name__)

def download3d():
    print(f"Starting Download.")

    now = datetime.now()
    time = "." + now.strftime("%Y_%m_%d-%H-%M-%S")
    folder_url = "https://mrms.ncep.noaa.gov/data/3DRefl/MergedReflectivityQC_"
    url_file_name = "/MRMS_MergedReflectivityQC_"
    file_extension = ".latest.grib2.gz"
    file_location = 'data/3Drefl/MergedReflectivityQC_'
    heights = ["00.50", "00.75", "01.00", "01.25", "01.50", "01.75", "02.00", "02.25", "02.50", "02.75", "03.00", "03.50", "04.00", "04.50", "05.00", "05.50", "06.00", "06.50", "07.00", "07.50", "08.00", "08.50", "09.00", "10.00", "11.00", "12.00", "13.00", "14.00", "15.00", "16.00", "17.00", "18.00", "19.00"]

    for height in heights:
        url = folder_url + height + url_file_name + height + file_extension
        location = file_location + height + time + file_extension
        unzip_location = location.replace(".gz", "")
        print(f"Downloading from url {url} into {file_location}")

        r = requests.get(url, allow_redirects=True)
        open(location, 'wb').write(r.content)

        with gzip.open(location, 'rb') as infile:
            with open(unzip_location, 'wb') as outfile:
                shutil.copyfileobj(infile, outfile)

    current_time = datetime.now().time()
    print(f"Latest files downloaded at {current_time}. Starting data processing and graph creation.")

    plotly_animated_volume.make_figure(downloadTime=time, h = 650, w = 1000)

    print(f"Finished downloading, processing, and graph creation.")

sched = BackgroundScheduler(daemon = True)
sched.add_job(download3d, 'interval', minutes=60)
sched.start()

@app.route('/')
def main():   

    timestamp = ".2023_06_16-16-15-32"
    file = "graphs/MRMS_3DRefl/" + timestamp + ".json"

    with open(file) as f:
        fig = plotly.io.read_json(f)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', 
        graphJSON = graphJSON, 
        title="MRMS Merged Reflectivity QC Data (MD)", 
        description=f"Source: https://mrms.ncep.noaa.gov/data/3DRefl/\nData recorded on {timestamp}"
    )

@app.route('/hello/<name>')
def hello(name):
    return (f'Hello {name}!')

if __name__ == '__main__':
    app.run()