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
config = json.load(open("config.json", "r")) # config.json import
<<<<<<< HEAD
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
=======
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea

# returns every date that the file system contains
def get_valid_dates():
    # return file system folders
    folder_2D = config["2D"]["graphs"]
    folder_3D = config["3D"]["graphs"]
<<<<<<< HEAD
<<<<<<< HEAD

    # create list of every date in the 2D folder
    files_2D = os.listdir(folder_2D)
    dates_2D = [file[0:-5] for file in files_2D] # only grab dated part

    # create list of every date in the 3D folder
    files_3D = os.listdir(folder_3D)
    dates_3D = [file[0:-5] for file in files_3D] # only grab dated part

    # create list of only the dates that are in both folders
    dates = [date for date in dates_2D if date in dates_3D]

    return dates 

=======
=======
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea

    # create list of every date in the 2D folder
    files_2D = os.listdir(folder_2D)
    dates_2D = [file[0:-5] for file in files_2D] # only grab dated part

    # create list of every date in the 3D folder
    files_3D = os.listdir(folder_3D)
    dates_3D = [file[0:-5] for file in files_3D] # only grab dated part

    # create list of only the dates that are in both folders
    dates = [date for date in dates_2D if date in dates_3D]

    print(dates)
    return dates 
    
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

# delete all files in a directory (used after graphs are created to empty data folders)
def delete_dir(dir):
    try:
        for f in os.listdir(dir): # iterate through every file in dir
            os.remove(os.path.join(dir, f)) # remove file with path dir/f

        print(f"Deleted files in directory {dir}")
    except ValueError:
        return "error in delete_dir"

<<<<<<< HEAD
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
=======
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
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
<<<<<<< HEAD
    files = os.listdir(dir)
    paths = [os.path.join(dir, file) for file in files]

    file = max(paths, key=os.path.getctime) # returns path with newest creation time
=======
    try:
        files = os.listdir(dir)
        paths = [os.path.join(dir, file) for file in files]

        file = max(paths, key=os.path.getctime) # returns path with newest creation time

        with open(file) as f:
            fig = plotly.io.read_json(f)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        print(f"Got graph at {dir}")

        return graphJSON
    except ValueError:
        return "Error with get_newest_graph"

def download(url, location):
    print(f"Downloading from url {url} into {location}")

    unzip_location = location.replace(".gz", "").replace(".latest", "")
<<<<<<< HEAD
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea

    with open(file) as f:
        fig = plotly.io.read_json(f)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    print(f"Got graph at {dir}")

<<<<<<< HEAD
    return graphJSON
=======
=======

    r = requests.get(url, allow_redirects=True)
    open(location, 'wb').write(r.content)

    with gzip.open(location, 'rb') as infile:
        with open(unzip_location, 'wb') as outfile:
            shutil.copyfileobj(infile, outfile)

>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
    return unzip_location

def create_figure(graph_type, file_time, h, w):
    if graph_type == "3Drefl":
        fig = plotly_volume.make_figure(download_time=file_time, h = 750, w = 1000)
    elif graph_type == "3Danim":
        fig = plotly_volume_animation.make_figure(download_time=file_time, h = 750, w = 1000)
    elif graph_type == "2Dprecip":
        fig = plotly_heatmap.make_figure(download_time=file_time, h = 750, w = 1000)

    file = f"graphs/{graph_type}/{file_time[1:-3]}.json"
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

        file_time = find_newest_time("2D")
        create_figure("2Dprecip", file_time, h=750, w=1000)

        print(f"Finished 2D graph creation at {file_time}. {vals_greater_0} values greater than 0 found")
        return vals_greater_0
    except ValueError:
        return "error in check_2d"

def download_3d():
    try:
        print(f"Starting Scheduled Download.")

        now = datetime.now()
        val_threshold = 0

        folder_url = config['3D']['url']
        url_file_name = config['3D']['file']
        file_extension = config['3D']['extension']
        file_location = config['3D']['file_location']
        file_name = config['3D']['file_name']
        heights = config['3D']['heights']
        file_time = find_newest_time("3D")

        if check_2d(file_time) <= 49: # check if there are at least 50 points to graph
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
<<<<<<< HEAD
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
=======
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea

@app.route('/')
def main():
    try:
        return render_template('index.html', 
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
            title="Overview", 
            content="description",
            reflJSON=None,
            animJSON=None,
            precipJSON=None,
<<<<<<< HEAD
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
=======
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
            valid_dates=get_valid_dates()
        )
    except ValueError:
        return "error in main"

@app.route('/graph_by_date/<date>', methods=['POST', 'GET'])
def return_dated_graph(date):
    if request.method == 'POST':
        print("received graph_by_date post request")

<<<<<<< HEAD
<<<<<<< HEAD
        refl = get_dated_graph('/home/lanceu/server/graphs/3Drefl', date)
        anim = get_dated_graph('/home/lanceu/server/graphs/3Danim', date)
        precip = get_dated_graph('/home/lanceu/server/graphs/2Dprecip', date)        

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

        refl = get_newest_graph('/home/lanceu/server/graphs/3Drefl')
        anim = get_newest_graph('/home/lanceu/server/graphs/3Danim')
        precip = get_newest_graph('/home/lanceu/server/graphs/2Dprecip')

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
=======
=======
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
        refl = get_dated_graph('graphs/3Drefl', date)
        anim = get_dated_graph('graphs/3Danim', date)
        precip = get_dated_graph('graphs/2Dprecip', date)        

        rendered_template = render_template(
            'index.html',
            title="temp",
            content=f"{date}",
            reflJSON=refl,
            animJSON=anim,
            precipJSON=precip,
            valid_dates=get_valid_dates()
        )

        return jsonify({'rendered_template': rendered_template})
    
@app.route('/graph_latest', methods=['POST', 'GET'])  
def return_latest_graph():
    try:
        if request.method == 'POST':
            print("received graph_latest post request")

            # refl = get_newest_graph('graphs/3Drefl')
            anim = get_newest_graph('graphs/3Danim')
            precip = get_newest_graph('graphs/2Dprecip')

            print("post made it here")

            rendered_template = render_template(
                'index.html',
                title="Latest Graphs",
                content="Description",
                reflJSON=None,
                animJSON=anim,
                precipJSON=precip,
                valid_dates=get_valid_dates()
            )

            return jsonify({'rendered_template': rendered_template})
    except ReferenceError as e:
        return "Erorr in return_latest_graph"

sched = BackgroundScheduler(daemon = True)
sched.add_job(download_3d, 'interval', minutes = 60)
<<<<<<< HEAD
sched.start()
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
=======
sched.start()
>>>>>>> 171ada4ad4dd1e64b822c0393487e39b2d7a05ea
