# flask imports
from flask import Flask, render_template, request, url_for, redirect, session

# 3dvissys imports
from . import vissys
from .utils import get_valid_dates, get_dated_graph, get_newest_graph

stringify = {
    '2Dprecip': 'Precipitation Heatmap',
    '3Drefl': 'Reflectivity Volume Plot',
    '3Danim': 'Reflectivity Volume Animation',
}

@vissys.route('/')
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

@vissys.route('/3Drefl/<date>', methods=['GET'])
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

@vissys.route('/3Danim/<date>', methods=['GET'])
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

@vissys.route('/2Dprecip/<date>', methods=['GET'])
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

@vissys.route('/graph/<graph_type>/<date>', methods=['GET'])
def route_dated_graph(graph_type, date):
    """
    Route for a dated graph of any type. Routes to specific graph type
    query routes and includes the target date. Called by JavaScript
    requesting the graph type and date in a URL. /graph/<graph_type>/<date>
    is the URL that will show up in the user's browser.
    """
    if request.method == 'GET':
        if graph_type == "3Drefl":
            return redirect(url_for('vissys.route_3Drefl', date=date))
        elif graph_type == "3Danim":
            return redirect(url_for('vissys.route_3Danim', date=date))
        elif graph_type == "2Dprecip":
            return redirect(url_for('vissys.route_2Dprecip', date=date))
    
@vissys.route('/graph/<graph_type>/latest', methods=['GET'])  
def route_newest_graph(graph_type):
    """
    Route for the latest graph of any type. Routes to specific graph type
    query routes and includes the "latest" date. Called by JavaScript
    requesting the graph type and date in a URL. /graph/<graph_type>/<latest
    is the URL that will show up in the user's browser.
    """
    if request.method == 'GET':
        if graph_type == "3Drefl":
            return redirect(url_for('vissys.route_3Drefl', date="latest"))
        elif graph_type == "3Danim":
            return redirect(url_for('vissys.route_3Danim', date="latest"))
        elif graph_type == "2Dprecip":
            return redirect(url_for('vissys.route_2Dprecip', date="latest"))