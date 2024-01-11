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

# other project file imports
import plotly_heatmap
import plotly_volume
import plotly_volume_animation

config = json.load(open("/home/lanceu/server/config.json", "r")) # all paths need to be fully directed for cronjobs

# delete all files in a directory (used after graphs are created to empty data folders)
def delete_dir(dir):
    try:
        for f in os.listdir(dir): # iterate through every file in dir
            os.remove(os.path.join(dir, f)) # remove file with path dir/f

        print(f"Deleted files in directory {dir}")
    except ValueError:
        return "error in delete_dir"

def download(url, location):
    print(f"Downloading from url {url} into {location}")

    unzip_location = location.replace(".gz", "").replace(".latest", "")

    r = requests.get(url, allow_redirects=True)
    open(location, 'wb').write(r.content)

    with gzip.open(location, 'rb') as infile:
        with open(unzip_location, 'wb') as outfile:
            shutil.copyfileobj(infile, outfile)

    return unzip_location

# used to generate a time to designate to each graph's file
def find_newest_time(data_type):
    # request file repository for 2D or 3D MRMS data
    url = config[data_type]["repository"]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # find all rows, go to second to last tr and td, strip text
    rows = soup.find('body').find('table').find_all("tr")
    newest_time = rows[len(rows) - 2].find_all("td")[1].text.strip()

    # create datetime object from string format
    input_format = "%d-%b-%Y %H:%M"
    dt_object = datetime.strptime(newest_time, input_format)

    # reconvert back into new string format
    output_format = "_%Y-%m-%d_%H-%M"
    formatted_string = dt_object.strftime(output_format)

    return formatted_string

def create_figure(graph_type, file_time, h, w):
    if graph_type == "3Drefl":
        fig = plotly_volume.make_figure(download_time=file_time, h = 750, w = 1000)
    elif graph_type == "3Danim":
        fig = plotly_volume_animation.make_figure(download_time=file_time, h = 750, w = 1000)
    elif graph_type == "2Dprecip":
        fig = plotly_heatmap.make_figure(download_time=file_time, h = 750, w = 1000)

    file = f"/home/lanceu/server/graphs/{graph_type}/{file_time[1:-3]}.json"
    with open(file, 'w') as f:
        f.write(plotly.io.to_json(fig))

# checks if there is substantial rain data using smaller 2d file; if True collect 3D data files and create 3D graph
def check_2d(file_time):
    try:
        url = config['2D']['url']
        file = config['2D']['file_location'] + config['2D']['file']

        unzip_location = download(url, file)

        grb = pygrib.open(unzip_location)
        data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)
        vals_greater_0 = (data > 0).sum()

        if vals_greater_0 <= 49: 
            print(f"Skipping 2D graph creation at {file_time}. {vals_greater_0} values greater than 0 found")
            return False

        file_time = find_newest_time("2D")
        create_figure("2Dprecip", file_time, h=750, w=1000)

        print(f"Finished 2D graph creation at {file_time}. {vals_greater_0} values greater than 0 found")
        return True
    except ValueError:
        return "error in check_2d"

def download_3d():
    try:
        print(f"Starting scheduled download")

        now = datetime.now()
        val_threshold = 0

        folder_url = config['3D']['url']
        url_file_name = config['3D']['file']
        file_extension = config['3D']['extension']
        file_location = config['3D']['file_location']
        file_name = config['3D']['file_name']
        heights = config['3D']['heights']
        file_time = find_newest_time("3D")

        if check_2d(file_time) is False: # check if there are at least 50 points to graph
            print("Skipping 3D graph creation.")
            return

        for height in heights:
            url = folder_url + height + url_file_name + height + file_extension
            location = file_location + file_name + height + file_time + file_extension

            download(url, location)

        create_figure("3Drefl", file_time, h=750, w=1000)

        create_figure("3Danim", file_time, h=750, w=1000)

        delete_dir(file_location)

        current_time = datetime.now().time()
        print(f"Finished 3D graph creation at {current_time}.")
    except ValueError:
        return "error in download_3d"    

if __name__ == "__main__":
    download_3d()