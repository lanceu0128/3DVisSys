# flask imports
from flask import Flask, render_template, request, jsonify, url_for
from apscheduler.schedulers.background import BackgroundScheduler

# python library imports
from datetime import datetime
import gzip, shutil, os, json, requests, time

# external library imports
import plotly, pygrib
import pandas as pd
from bs4 import BeautifulSoup
<<<<<<< HEAD
<<<<<<< HEAD

app = Flask(__name__)
config = json.load(open("/home/lanceu/server/config.json", "r")) # all paths need to be fully directed for cronjobs
=======
=======
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea

# other project file imports
import plotly_heatmap
import plotly_volume
import plotly_volume_animation

app = Flask(__name__)
latest_data_url = "https://mrms.ncep.noaa.gov/data/2D/PrecipRate/MRMS_PrecipRate.latest.grib2.gz"
file_location = 'data/MRMS_PrecipRate.latest.grib2.gz'

@app.route('/')
def main():
    return 'Hello World'

@app.route('/download/latest')
def download():
    r = requests.get(latest_data_url, allow_redirects=True)
    open(file_location, 'wb').write(r.content)

    with gzip.open(file_location, 'rb') as infile:
        with open('data/MRMS_PrecipRate.latest.grib2', 'wb') as outfile:
            shutil.copyfileobj(infile, outfile)

    return "Downloading File"

@app.route('/hello/<name>')
def hello(name):
    return (f'Hello {name}!')

if __name__ == '__main__':
    app.run()