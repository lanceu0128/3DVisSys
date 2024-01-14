# flask imports
from flask import Flask, render_template, request, jsonify, url_for

# python library imports
from datetime import datetime
import gzip, shutil, os, json, requests, time

# external library imports
import plotly, pygrib
import pandas as pd
from bs4 import BeautifulSoup

app = Flask(__name__)
config = json.load(open("/data3/lanceu/server/config.json", "r")) # all paths need to be fully directed for cronjobs

# returns every date that the file system contains
def get_valid_dates():
    # return file system folders
    folder_2D = config["2D"]["graphs"]
    folder_3D = config["3D"]["graphs"]

    # create list of every date in the 2D folder
    files_2D = os.listdir(folder_2D)
    dates_2D = [file[0:-5] for file in files_2D] # only grab dated part

    # create list of every date in the 3D folder
    files_3D = os.listdir(folder_3D)
    dates_3D = [file[0:-5] for file in files_3D] # only grab dated part

    # create list of only the dates that are in both folders
    dates = [date for date in dates_2D if date in dates_3D]

    return dates 

# returns graph from input directory and date (used for "Get Graph from Selected Date" button functionality)
def get_dated_graph(dir, target_date):
    print(f"Grabbing graph at {dir} for time {target_date}")

    # get all dates and convert to date_objects
    date_strings = get_valid_dates()
    date_objs = [datetime.strptime(date_string, "%Y-%m-%d_%H") for date_string in date_strings]

    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d_%H-%M") # convert target to date object

    # grab closest date and convert to string
    closest_date_obj = min(date_objs, key=lambda d: abs(d - target_date_obj)) # grab date with lowest distance from target
    closest_date_string = closest_date_obj.strftime("%Y-%m-%d_%H")
        
    # find file path 
    file = "/" + closest_date_string + ".json"
    path = dir + file

    # read file and return
    with open(path) as f:
        fig = plotly.io.read_json(f)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    print(f"Got graph at {path}")

    return graphJSON

# returns newest graph in input directory (used for "Get Latest Graph" button functionality)
def get_newest_graph(dir):
    files = os.listdir(dir)
    paths = [os.path.join(dir, file) for file in files]

    file = max(paths, key=os.path.getctime) # returns path with newest creation time

    with open(file) as f:
        fig = plotly.io.read_json(f)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    print(f"Got graph at {dir}")

    return graphJSON

@app.route('/')
def main():
    try:
        return render_template('index.html', 
            valid_dates=get_valid_dates()
        )
    except ValueError:
        return "error in main"

@app.route('/graph_by_date/<date>', methods=['POST', 'GET'])
def return_dated_graph(date):
    if request.method == 'POST':
        print("received graph_by_date post request")

        refl = get_dated_graph('/data3/lanceu/graphs/3Drefl', date)
        anim = get_dated_graph('/data3/lanceu/graphs/3Danim', date)
        precip = get_dated_graph('/data3/lanceu/graphs/2Dprecip', date)        

        rendered_template = render_template(
            'graphs.html',
            title="Graphs by Date",
            reflJSON=refl,
            animJSON=anim,
            precipJSON=precip,
            valid_dates=get_valid_dates()
        )

        return jsonify({'rendered_template': rendered_template})
    
@app.route('/graph_latest', methods=['POST', 'GET'])  
def return_latest_graph():
    if request.method == 'POST':
        print("received graph_latest post request")

        refl = get_newest_graph('/data3/lanceu/graphs/3Drefl')
        anim = get_newest_graph('/data3/lanceu/graphs/3Danim')
        precip = get_newest_graph('/data3/lanceu/graphs/2Dprecip')

        date = get_valid_dates()
        date = date[len(date)-1]

        rendered_template = render_template(
            'graphs.html',
            title="Latest Graphs",
            content=f"{date}",
            htmlCard=None,
            reflJSON=refl,
            animJSON=anim,
            precipJSON=precip,
            valid_dates=get_valid_dates()
        )

        return jsonify({'rendered_template': rendered_template})