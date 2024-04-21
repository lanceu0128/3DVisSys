# python library imports
from datetime import datetime, timedelta
import gzip, shutil, os, json, requests, time, re, uuid

# external library imports
import plotly, pygrib
import pandas as pd
from bs4 import BeautifulSoup

def get_valid_dates():
    """
    Returns every date contained in the app file system.
    Finds dates based on regex matching for dates in a certain folder
    and returns every date contained in the folder.
    """

    # return file system folders
    folder_2D = "/data3/lanceu/graphs/2Dprecip"
    folder_3D = "/data3/lanceu/graphs/3Drefl"
    # naming convention used for newest files; using to ignore the old files
    file_pattern = re.compile(r'^\d{8}-\d{4}\.json$')

    # create list of every date in the 2D folder
    files_2D = os.listdir(folder_2D)
    dates_2D = [file[0:-5] for file in files_2D if file_pattern.match(file)] # only grab dated part

    # create list of every date in the 3D folder
    files_3D = os.listdir(folder_3D)
    dates_3D = [file[0:-5] for file in files_3D if file_pattern.match(file)] # only grab dated part

    # create list of only the dates that are in both folders
    dates = [date for date in dates_2D if date in dates_3D]

    return dates 

def get_dated_graph(dir, target_date):
    """
    Takes a directory of graphs and a target date,
    returns queried graph from input directory that matches the date.
    (used for "Get Graph from Selected Date" button functionality)
    """

    # get all dates and convert to date_objects
    date_strings = get_valid_dates()
    date_objs = [datetime.strptime(date_string, "%Y%m%d-%H%M") for date_string in date_strings]

    target_date_obj = datetime.strptime(target_date, "%Y%m%d-%H%M") # convert target to date object

    # grab closest date and convert to string
    closest_date_obj = min(date_objs, key=lambda d: abs(d - target_date_obj)) # grab date with lowest distance from target
    closest_date_string = closest_date_obj.strftime("%Y%m%d-%H%M")
        
    # find file path 
    file = "/" + closest_date_string + ".json"
    path = dir + file

    # read file and return
    with open(path) as f:
        fig = plotly.io.read_json(f)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    print(f"Got graph at {path}")

    return graphJSON

def get_newest_graph(dir):
    """
    Takes a directory and returns the newest graph in the input directory.
    Works by simply getting the graph that is the most recently created. 
    May cause issues if old graphs are generated for testing recently.
    (used for "Get Latest Graph" button functionality)
    """

    files = os.listdir(dir)
    paths = [os.path.join(dir, file) for file in files]

    file = max(paths, key=os.path.getctime) # returns path with newest creation time

    with open(file) as f:
        fig = plotly.io.read_json(f)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    print(f"Got graph at {dir}")

    return graphJSON