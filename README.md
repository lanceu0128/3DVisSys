# 3DVisSys
## Introduction
3DVisSys, or 3D Visualization System, is free open-source software for examining NOAA MRMS precipitation and reflectivity data with 3D interactive visualizations directly in the browser. It features a web application to load and interact with visualizations, as well as backend data pipelines that create those visualizations on a schedule. It was primarily built with Python 3.9, Flask and Plotly as part of a `cisess.umd.edu` summer internship.

## Live
A live version of 3DVisSys is being deployed soon!

## Running the App
For users who want to view and interact with visualizations, running in one's local environment can be done by installing all requirements and running the Flask app:

1. **Install all requirements:**
    - For Conda users: 
        1. (OPTIONAL) If you have previously installed this environment, go back to the base environment with `conda activate` and remove the previous installation `conda remove --name 3dvissys --all`.
        2. Run `conda env create -f environment.yml` and switch into the new environment with `conda activate 3dvissys`.
    - Pip users: Run `pip install -r requirements.txt`.

2. **Switch into the app directory and run the app:**
    1. From the root directory, run `cd app`.
    2. Run `flask run`.

## Running the Data Pipelines
For users who want to try creating their own visualizations, running in one's local environment can be done by installing all requirements and running the server directory:

1. **Install all requirements:**
    - For Conda users: 
        1. If you have previously installed this environment, go back to the base environment with `conda activate` and remove the previous installation `conda remove --name 3dvissys --all`.
        2. Run `conda env create -f environment.yml` and switch into the new environment.
    - For Pip users: Run `pip install -r requirements.txt`.

2. **Switch into the server directory and run the server:**
    1. From the root directory, run `cd server`.
    2. Run `python scripts.py` to create graphs for the current time. Users may also want to use cronjob or another scheduler to run the file at certain times. An example crontab used in development to run the script hourly can be found in `server/cronjob.txt`.
  
## Tech Stack
3DVisSys was primarily built with the following technologies:
- Python
    - Flask
        - Flask-MonitoringDashboard
    - Pandas
    - NumPy
    - SciPy
    - Plotly
    - BeautifulSoup
- HTML
- CSS
    - Bootstrap
        - Bootstrap Tempus Dominus Widget
- JavaScript
    - React.js
- Linux (High-Performance Computing Server) 

A more detailed view can be found in either `environment.yml` or `requirements.txt`.
