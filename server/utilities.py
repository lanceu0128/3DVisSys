from multiprocessing import Pool
from geopy.geocoders import Nominatim
import numpy as np
import pandas as pd
import time, json, urllib, requests, logging
import plotly, pygrib, netCDF4
import plotly.graph_objects as go
from scipy.interpolate import griddata
from matplotlib import cm
from matplotlib.colors import ListedColormap, colorConverter

heights = ["00.50", "00.75", "01.00", "01.25", "01.50", "01.75", "02.00", "02.25", "02.50", "02.75", "03.00", "03.50", "04.00", "04.50", "05.00", "05.50", "06.00", "06.50", "07.00", "07.50", "08.00", "08.50", "09.00", "10.00", "11.00", "12.00", "13.00", "14.00", "15.00", "16.00", "17.00", "18.00", "19.00"]
file_location = '/data3/lanceu/server/data/3Drefl/'
# file_location = '/data3/lanceu/server/testdata/SampleData/' # uncomment if testing from this file
file_time = ""
file_name = 'MRMS_MergedReflectivityQC_'
file_extension = '.grib2'
start_time = time.time()

logging.basicConfig(level=logging.INFO, filename="/data3/lanceu/server/log.log", filemode="a",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def process_height_data(height):
    '''
    Processes pygrib file for a singular height level. 
    Needs to be it's own function for the multiprocessing pool to easily divide and conquer.
    Input: height level being used
    Output: dataframe

    todo: there's probably better ways to divide the pool
    '''

    logging.debug(f"Processing {height} level data")

    grb = pygrib.open(file_location + file_name + height + file_time + file_extension)
    data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)

    data[data < 0] = 0 # forgot why this is here?
    lons -= 360 # +- 360 needed for weird grib file format from MRMS

    # pool arrays to reduce size - might not be needed to this degree for 2D heatmaps though? 
    # flatten arrays for easy dataframe usage
    pooled_lats = pool_array(lats, 5, 5).flatten()
    pooled_lons = pool_array(lons, 5, 5).flatten()
    pooled_data = pool_array(data, 5, 5).flatten()
    # get locations for our coordinates from stored API output
    locations = get_locations(pooled_lats, pooled_lons)
    # make heights array with the same shape as the others
    heights = np.full(pooled_data.shape, float(height))

    df_dict = {"lat": pooled_lats, "lon": pooled_lons, "data": pooled_data, "locations": locations, "heights": heights}
    df = pd.DataFrame(df_dict)

    runtime = time.time() - start_time
    logging.debug(f"Finished processing %s data in %s.", height, str(runtime))

    return df

def grab_data(download_time, graph_type = "unnamed"):
    '''
    Processes 3D volume map data from pygrib file and outputs a dataframe.
    Uses multiprocessing to divide heights levels by processes, huge speed-up.  

    Input:
    - graph_type: string for logging purposes only (3D animation, 3D reflectivity, etc.)
    '''
    global file_time
    file_time = download_time

    logging.info("Starting %s data processing and multiprocessing.", graph_type)
    # start 28 processes (the max on Odin) and have them work on each height in heights
    # todo: make this adaptable to whatever server this will be installed on
    pool = Pool(28)
    height_frames = pool.map(process_height_data, heights) 

    df = pd.concat(height_frames, ignore_index=True, sort=False)
    logging.info("Finished volume processing data for all heights. Final data:")
    logging.info("\n %s", df.describe())
    return df

def pool_array(data, pool_size, stride, max=False):
    '''
    Takes 2D arrays and uses mean/max pooling.
    Used in graph creation tools to reduce size of graphs for performance.
    Input: 
    data - 2D numpy array
    pool_size - size of pools 
    stride - distance between pools
    max - whether we want to use mean or max
    Output: 2D numpy array fully processed for mean/max pooling
    '''
    pools = []
    pooled = []

    for i in np.arange(data.shape[0], step=stride):
        for j in np.arange(data.shape[1], step=stride):
            pool = data[i:i+pool_size, j:j+pool_size]
            pools.append(pool) # array of pools prior to mean/min/maxing
    
    new_shape = (int(data.shape[0] / pool_size), int(data.shape[1] / pool_size)) 

    for pool in pools: # make new pooled array as Python array first to append first
        if max == False:
            pooled.append(round(np.mean(pool), 5)) # can be changed to min, max, or mean; rounded by 3 significant figures
        else:
            pooled.append(round(np.max(pool), 10))
        
    return np.array(pooled).reshape(new_shape) # convert to NumpyArray and reshape


# function taken from the plotly documentation; converts matplotlib colormaps to plotly colorscales
def matplotlib_to_plotly(cmap, pl_entries):
    '''
    Converts matplotlib colormaps to plotly colorscales.
    Taken directly from: https://plotly.com/python/v3/matplotlib-colorscales/
    Input: The colormap you want to convert and the number of colors
    Output: Plotly colorscale for use in Plotly graphs
    '''
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale

def elevation_map():
    '''
    Creates elevation map and ocean map frames for use in 3D graphs. 
    Takes dem_conus.nc and does a LOT of fancy numpy stuff to make it usable.
    Output: two Plotly frames. 

    note: ocean map is not currently used in the graphs because it's ugly
    '''
    f=netCDF4.Dataset('/data3/lanceu/server/dem_conus.nc',"r")
    lat_dem=f.variables['lat'][:]
    lon_dem=f.variables['lon'][:]
    dem = f.variables['dem'][:]
    
    dem = dem / 1000 # convert m to km
    lat_mesh, lon_mesh = np.meshgrid(lat_dem, lon_dem, indexing='ij') # stitch data together

    # create boolean masks to remove out of bounds data
    lat_min, lat_max = 37.0, 40.0
    lon_min, lon_max = -80.0, -75.0
    lat_mask = (lat_mesh >= lat_min) & (lat_mesh <= lat_max)
    lon_mask = (lon_mesh >= lon_min) & (lon_mesh <= lon_max)

    # apply masks to all three arrays
    filtered_lat = lat_mesh[lat_mask & lon_mask]
    filtered_lon = lon_mesh[lat_mask & lon_mask]
    filtered_dem = dem[lat_mask & lon_mask]

    # create a grid for interpolation
    interpolation_count = 200 # amount to interpolate by; higher increases "resolution" of terrain
    dense_lon = np.linspace(filtered_lon.min(), filtered_lon.max(), interpolation_count) 
    dense_lat = np.linspace(filtered_lat.min(), filtered_lat.max(), interpolation_count)
    grid_lon, grid_lat = np.meshgrid(dense_lon, dense_lat)

    # interpolate elevation data on a grid
    interpolated_dem = griddata((filtered_lon, filtered_lat), filtered_dem, (grid_lon, grid_lat), method='linear')

    # create color map based on realistic terrain
    terr = cm.get_cmap('terrain', 64)
    newcolors = terr(np.linspace(0, 1, 50))
    newcolors1 = terr(np.linspace(0, 1, 64))
    newcolors[:, :] = newcolors1[14:64,:]
    terrain_cmp = ListedColormap(newcolors)
    terrain_cmp = matplotlib_to_plotly(terrain_cmp, 255)

    # making graph object
    elevation_map = go.Surface(
        x = grid_lat, 
        y = grid_lon, 
        z = interpolated_dem, 
        hovertemplate = "Latitude: %{x:.3f} <br>Longitude: %{y:.3f} <br>Elevation: %{z:.3f} km <br><extra></extra>",
        colorscale = terrain_cmp,
        colorbar = dict(
            title = "Elevation",
            thickness = 20,
            ticklen = 0, 
            tickcolor = 'black',
            tickfont = dict(size=14, color='black'),
            x = -0.1
        )
    )

    # build ocean layer to complement elevation, fill empty space
    ocean_lat = [lat_min, lat_min, lat_max, lat_max]
    ocean_lon = [lon_min, lon_min, lon_max, lon_max]
    ocean_height = [[0.0001, 0.0001, 0.0001, 0.0001], [0.0001, 0.0001, 0.0001, 0.0001], [0.0001, 0.0001, 0.0001, 0.0001], [0.0001, 0.0001, 0.0001, 0.0001]]
    ocean_map = go.Surface(x=ocean_lat, y=ocean_lon, z=ocean_height, showscale=False, colorscale="PuBuGn")

    return elevation_map, ocean_map

def get_locations(lats, lons):
    '''
    Takes the locations_rounded.json file puts it into a usable list of locations.

    todo: the graphs show incorrect locations and i'm not sure why
    '''
    global locations

    locs = []

    # locations_rounded contains JSON file with location data rounded to make grabbing data easier
    with open('/data3/lanceu/server/locations_rounded.json', 'r') as file:
        locations = json.load(file)

    # grab county data from each coordinate in flattened 2D array
    for i in range(len(lats)):
        try:
            loc = locations[str(lats[i])][str(lons[i])]['county']
            locs.append(loc)
        except:
            locs.append("")

    return locs