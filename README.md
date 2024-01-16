# 3DVisSys
## Introduction
3DVisSys, or 3D Visualization System, is free open-source software for examining NOAA MRMS precipitation and reflectivity data with 3D interactive visualizations directly in the browser. It features a web application to load and interact with visualizations, as well as backend data pipelines that create those visualizations 24/7. It was primarily built with Python 3.9, Flask and Plotly. 

## Instructions
### Running the App
For users who want to view and interact with graphs, running in one's local envrionment an be done by installing all requirements and running the Flask app:

1. Install all requirements:
    a. For Conda users: Run `conda env create -f environment.yml` and switch into the new environment.
    b. Pip users: Run `pip install -r requirements.txt`

2. Switch into the app directory and run:
    i. From the root directory, run `cd app`
    ii. Run `Flask run`

### Running the Backend
For users who want to try running the backend pipelines themselves, running in one's local environment can be done by installing all requirements and running the server directory:

1. Install all requirements:
    a. For Conda users: Run `conda env create -f environment.yml` and switch into new environment.
    b. For Pip users: Run `pip install -r requirements.txt`
2. Switch into server directory and run:
    i. From the root directory, run `cd app`
    ii. Run `python scripts.py` or create a crontab to run the file on a desired schedule.
