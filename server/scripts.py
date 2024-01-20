# python library imports
from datetime import datetime
import gzip, shutil, os, json, requests, time, logging

# external library imports
import plotly, pygrib
import pandas as pd
from bs4 import BeautifulSoup

# other project file imports
import plotly_heatmap
import plotly_volume
import plotly_volume_animation

logging.basicConfig(level=logging.INFO, filename="/data3/lanceu/server/log.log", filemode="a",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

config = json.load(open("/data3/lanceu/server/config.json", "r")) # all paths need to be fully directed for cronjobs

# delete all files in a directory (used after graphs are created to empty data folders)
def delete_dir(dir):
    try:
        logging.info(f"Cleaning used data files in directory %s.", dir)
        
        for f in os.listdir(dir): # iterate through every file in dir
            os.remove(os.path.join(dir, f)) # remove file with path dir/f

        logging.info(f"Cleaned files in directory %s.", dir)
    except Exception as e:
        logging.exception("EXCEPTION in delete_dir():")

def download(url, location):
    try:
        logging.debug(f"Downloading data from url %s into %s.", url, location)

        unzip_location = location.replace(".gz", "").replace(".latest", "")

        r = requests.get(url, allow_redirects=True)
        open(location, 'wb').write(r.content)

        with gzip.open(location, 'rb') as infile:
            with open(unzip_location, 'wb') as outfile:
                shutil.copyfileobj(infile, outfile)

        logging.debug(f"Download successful.")

        return unzip_location
    except Exception as e:
        logging.exception("EXCEPTION in download():")

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

def create_figure(graph_type, file_time):
    try:
        logging.info("Creating figure for graph type %s and time %s.", graph_type, file_time)

        if graph_type == "3Drefl":
            fig = plotly_volume.make_figure(download_time=file_time, h=750, w=1000)
        elif graph_type == "3Danim":
            fig = plotly_volume_animation.make_figure(download_time=file_time, h=750, w=1000)
        elif graph_type == "2Dprecip":
            fig = plotly_heatmap.make_figure(download_time=file_time, h=750, w=1000)

        path = f"/data3/lanceu/graphs/{graph_type}/{file_time[1:-3]}.json"
        with open(path, 'w') as f:
            f.write(plotly.io.to_json(fig))

        logging.info("Figure creation successful. File stored in %s.", path)
    except Exception as e:
        logging.exception("EXCEPTION in create_figure():")

# checks if there is substantial rain data using smaller 2d file; if True collect 3D data files and create 3D graph
def check_2d(file_time):
    try:
        logging.info("Checking for substantial precipitation data during time %s.", file_time)

        url = config['2D']['url']
        file = config['2D']['file_location'] + config['2D']['file']

        unzip_location = download(url, file)

        grb = pygrib.open(unzip_location)
        data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)
        vals_greater_0 = (data > 0).sum()

        if vals_greater_0 <= 49: 
            logging.info("%d values greater than 0 found. Skipping 2D graph creation for %s.", vals_greater_0, file_time)
            return False

        file_time = find_newest_time("2D")
        create_figure("2Dprecip", file_time)

        logging.info("%d values greater than 0 found. Finished 2D graph creation for %s.", vals_greater_0, file_time)
        return True
    except Exception as e:
        logging.exception("EXCEPTION in check_2d:")

# basically the "__main__" function. checks for precipitation data and donwloads/visualizes reflectivity accordingly
def download_3d():
    try:
        logging.info("==========================================================================================")
        logging.info("Starting scheduled download.")

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
            logging.info("Not enough data. Skipping 3D graph creation.")
            return

        logging.info("Starting downloading of 3D reflectivity data.")

        for height in heights:
            url = folder_url + height + url_file_name + height + file_extension
            location = file_location + file_name + height + file_time + file_extension
            download(url, location)

        logging.info("Finished downloading of 3D reflectivity data.")

        create_figure("3Drefl", file_time)
        create_figure("3Danim", file_time)
        delete_dir(file_location)

        logging.info("Finished 3D graph creation.")
    except Exception as e:
        logging.exception("EXCEPTION in download_3d():")    

if __name__ == "__main__":
    download_3d()