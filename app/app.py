# flask imports
from flask import Flask, render_template, request, url_for, redirect, session
import flask_monitoringdashboard as dashboard

# python library imports
from datetime import datetime, timedelta
import gzip, shutil, os, json, requests, time, re, uuid

# external library imports
import plotly, pygrib
import pandas as pd
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'EastmostPeninsula'
app.permanent_session_lifetime = timedelta(days=1) # used to count each daily use as a unique visit
config = json.load(open("/data3/lanceu/server/config.json", "r")) # all paths need to be fully directed for cronjobs

stringify = {
    '2Dprecip': 'Precipitation Heatmap',
    '3Drefl': 'Reflectivity Volume Plot',
    '3Danim': 'Reflectivity Volume Animation',
}

def get_user_id():
    """
    Used for monitoring dashboard purposes only (can be removed).
    Generates a unique user ID for a session if user is not already in a 
    session. Returning users are kicked out of sessions after about 24 hours. 
    """

    if 'user_id' not in session:
        session.permanent = True
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

def get_valid_dates():
    """
    Returns every date contained in the app file system.
    Finds dates based on regex matching for dates in a certain folder
    and returns every date contained in the folder.
    """

    # return file system folders
    folder_2D = config["2D"]["graphs"]
    folder_3D = config["3D"]["graphs"]
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

@app.route('/')
def main():
    """
    3D Visualization System index route.
    """

    try:
        return render_template('index.html', 
            valid_dates=get_valid_dates(),
            graph_type="3Drefl" # default value
        )
    except ValueError:
        return "error in main"

@app.route('/3Drefl/<date>', methods=['GET'])
def route_3Drefl(date):
    """
    Route for any 3D reflectivity graph. Takes an input date, matches
    date with either target date or newest by calling get_newest_graph(dir, date) 
    or get_latest_graph(dir), then returning the JSON data in the return template. 
    Called from either route_dated_graph or route_newest_graph.
    """

    if request.method == "GET":
        # split based on whether we called from latest or a certain date
        if date == "latest":
            graph = get_newest_graph(f'/data3/lanceu/graphs/3Drefl')
        else:
            graph = get_dated_graph(f'/data3/lanceu/graphs/3Drefl', date)    

        return render_template(
            'graphs.html',
            title="Reflectivity",
            graphJSON=graph,
            valid_dates=get_valid_dates(),
            graph_type="3Drefl",
        )

@app.route('/3Danim/<date>', methods=['GET'])
def route_3Danim(date):
    """
    Route for any 3D animation graph. Takes an input date, matches
    date with either target date or newest by calling get_newest_graph(dir, date) 
    or get_latest_graph(dir), then returning the JSON data in the return template. 
    Called from either route_dated_graph or route_newest_graph.
    """

    if request.method == "GET":
        if date == "latest":
            graph = get_newest_graph(f'/data3/lanceu/graphs/3Danim')
        else:
            graph = get_dated_graph(f'/data3/lanceu/graphs/3Danim', date)       

        return render_template(
            'graphs.html',
            title="Reflectivity (Animation)",
            graphJSON=graph,
            valid_dates=get_valid_dates(),
            graph_type="3Danim",
        )

@app.route('/2Dprecip/<date>', methods=['GET'])
def route_2Dprecip(date):
    """
    Route for any 2D precipitation graph. Takes an input date, matches
    date with either target date or newest by calling get_newest_graph(dir, date) 
    or get_latest_graph(dir), then returning the JSON data in the return template. 
    Called from either route_dated_graph or route_newest_graph.
    """
    if request.method == "GET":
        if date == "latest":
            graph = get_newest_graph(f'/data3/lanceu/graphs/2Dprecip')
        else:
            graph = get_dated_graph(f'/data3/lanceu/graphs/2Dprecip', date)    

        return render_template(
            'graphs.html',
            title="Precipitation",
            graphJSON=graph,
            valid_dates=get_valid_dates(),
            graph_type="2Dprecip",
        )

@app.route('/graph/<graph_type>/<date>', methods=['GET'])
def route_dated_graph(graph_type, date):
    """
    Route for a dated graph of any type. Routes to specific graph type
    query routes and includes the target date. Called by JavaScript
    requesting the graph type and date in a URL. /graph/<graph_type>/<date>
    is the URL that will show up in the user's browser.
    """
    if request.method == 'GET':
        if graph_type == "3Drefl":
            return redirect(url_for('route_3Drefl', date=date))
        elif graph_type == "3Danim":
            return redirect(url_for('route_3Danim', date=date))
        elif graph_type == "2Dprecip":
            return redirect(url_for('route_2Dprecip', date=date))
    
@app.route('/graph/<graph_type>/latest', methods=['GET'])  
def route_newest_graph(graph_type):
    """
    Route for the latest graph of any type. Routes to specific graph type
    query routes and includes the "latest" date. Called by JavaScript
    requesting the graph type and date in a URL. /graph/<graph_type>/<latest
    is the URL that will show up in the user's browser.
    """
    if request.method == 'GET':
        if graph_type == "3Drefl":
            return redirect(url_for('route_3Drefl', date="latest"))
        elif graph_type == "3Danim":
            return redirect(url_for('route_3Danim', date="latest"))
        elif graph_type == "2Dprecip":
            return redirect(url_for('route_2Dprecip', date="latest"))

# needs to be at the bottom of the file for first time usage, gltiches out otherwise
dashboard.config.init_from(file='/data3/lanceu/app/monitoring/config.cfg')
dashboard.config.group_by = get_user_id
dashboard.bind(app)

if __name__ == '__main__':
    app.run()