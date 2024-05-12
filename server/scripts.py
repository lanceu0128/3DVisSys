# python library imports
from datetime import datetime
import gzip, shutil, os, json, requests, time, logging, re

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

def delete_dir(dir):
    '''
    Delete all files in a directory (used after graphs are created to empty data folders)
    Input: the dir string from root
    '''
    try:
        logging.info(f"Cleaning used data files in directory %s.", dir)
        
        for f in os.listdir(dir): # iterate through every file in dir
            os.remove(os.path.join(dir, f)) # remove file with path dir/f

        logging.info(f"Cleaned files in directory %s.", dir)
    except Exception as e:
        logging.exception("EXCEPTION in delete_dir():")

def download(url, location):
    '''
    Downloads data from a url into a location. Uses request and gzip to download and unzip.
    Input: url to download from and location to download into
    Output: where the unzipped file was stored (same as location but with different file type) 
    '''
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

def find_newest_time(data_type):
    '''
    Generates a time to designate to each graph's file. 
    Uses BS4 and RegEx to pattern match the newest file ending in 00 
    Input: data_type (either "2D" or "3D" to access precipitation or reflectivity)
    output: newest time in regex format _\d{8}-\d{6}
    '''
    # request file repository for 2D or 3D MRMS data
    url = config[data_type]["repository"]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    pattern = r'_\d{8}-\d{6}'

    total_files, total_matches = 0, 0

    for link in soup.find_all('a')[::-1]:
        filename = link.get('href')
        match = re.search(pattern, filename)
        if match:
            matched_string = match.group()  # extract the matched string
            if matched_string[-4:-2] == '00':  # check if start of the hour
                return matched_string

def create_figure(graph_type, file_time):
    '''
    Just calls the individual figure creation files to make a figure for a specific time.
    Input: graph_type ("2Dprecip", "3Drefl", "3Danim")

    todo: these files should probably go to classes for better organization within them
    todo: graph_type should be some kind of enum 
    '''
    try:
        logging.info("Creating figure for graph type %s and time %s.", graph_type, file_time)

        if graph_type == "3Drefl":
            fig = plotly_volume.make_figure(download_time=file_time, h=750, w=1000)
        elif graph_type == "3Danim":
            fig = plotly_volume_animation.make_figure(download_time=file_time, h=750, w=1000)
        elif graph_type == "2Dprecip":
            fig = plotly_heatmap.make_figure(download_time=file_time, h=750, w=1000)

        path = f"/data3/lanceu/graphs/{graph_type}/{file_time[1:-2]}.json"
        with open(path, 'w') as f:
            f.write(plotly.io.to_json(fig))

        logging.info("Figure creation successful. File stored in %s.", path)
    except Exception as e:
        logging.exception("EXCEPTION in create_figure():")

def check_2d(file_time):
    '''
    Checks if there is substantial rain data using smaller 2d file. 
    Used to determine if we should collect 3D data files and create 3D graph.
    '''
    try:
        logging.info("Checking for substantial precipitation data during time %s.", file_time)

        file_time = find_newest_time("2D")
        url = config['2D']['url'] + file_time + config['2D']['extension']
        file = config['2D']['file_location'] + config['2D']['file']

        unzip_location = download(url, file)

        grb = pygrib.open(unzip_location)
        data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)
        vals_greater_0 = (data > 0).sum()

        if vals_greater_0 <= 49: 
            logging.info("%d values greater than 0 found. Skipping 2D graph creation for %s.", vals_greater_0, file_time)
            return False

        create_figure("2Dprecip", file_time)

        logging.info("%d values greater than 0 found. Finished 2D graph creation for %s.", vals_greater_0, file_time)
        return True
    except Exception as e:
        logging.exception("EXCEPTION in check_2d:")

def download_3d():
    '''
    Basically the "__main__" function. Calls check_2d() and donwloads/visualizes precipitation and reflectivity accordingly.
    '''
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
            url = folder_url + height + url_file_name + height + file_time + file_extension
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