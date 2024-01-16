# 3DVisSys
## Introduction
3DVisSys, or 3D Visualization System, is free open-source software for examining NOAA MRMS precipitation and reflectivity data with 3D interactive visualizations directly in the browser. It features a web application to load and interact with visualizations, as well as backend data pipelines that create those visualizations on a schedule. It was primarily built with Python 3.9, Flask and Plotly. 

## Live
A live version of 3DVisSys is being deployed soon!

## Running the App
For users who want to view and interact with visualizations, running in one's local environment can be done by installing all requirements and running the Flask app:

1. **Install all requirements:**
    - For Conda users: Run `conda env create -f environment.yml` and switch into the new environment.
    - Pip users: Run `pip install -r requirements.txt`

2. **Switch into the app directory and run the app:**
    1. From the root directory, run `cd app`
    2. Run `Flask run`

## Running the Backend
For users who want to try creating their own visualizations, running in one's local environment can be done by installing all requirements and running the server directory:

1. **Install all requirements:**
    - For Conda users: Run `conda env create -f environment.yml` and switch into the new environment.
    - For Pip users: Run `pip install -r requirements.txt`

2. **Switch into the server directory and run the server:**
    1. From the root directory, run `cd server`
    2. Run `python scripts.py` or create a crontab to run the file on a desired schedule.
