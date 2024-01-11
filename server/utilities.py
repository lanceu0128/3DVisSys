from multiprocessing import Pool
from geopy.geocoders import Nominatim
import numpy as np
<<<<<<< HEAD
import pandas as pd
import time, json, urllib, requests
import plotly, pygrib, netCDF4
import plotly.graph_objects as go
from scipy.interpolate import griddata
from matplotlib import cm
from matplotlib.colors import ListedColormap, colorConverter
=======
import pygrib, time, json, urllib, requests
>>>>>>> 3DVisSys/main

start_time = time.time()
locations = {}

file_location = '/home/lanceu/server/testdata/SampleData/'
file_name = 'MRMS_MergedReflectivityQC_'
file_extension = "_20210708-120040" +'.grib2'
height = "00.50" # any height will work for location data

# takes large arrays and creates smaller array of 5x5 means of original
<<<<<<< HEAD
def pool_array(data, pool_size, stride, max=False):
=======
def pool_array(data, pool_size, stride):
>>>>>>> 3DVisSys/main
    pools = []
    pooled = []

    for i in np.arange(data.shape[0], step=stride):
        for j in np.arange(data.shape[1], step=stride):
            pool = data[i:i+pool_size, j:j+pool_size]
            pools.append(pool) # array of pools prior to mean/min/maxing
    
    new_shape = (int(data.shape[0] / pool_size), int(data.shape[1] / pool_size)) 

    for pool in pools: # make new pooled array as Python array first to append first
<<<<<<< HEAD
        if max == False:
            pooled.append(round(np.mean(pool), 5)) # can be changed to min, max, or mean; rounded by 3 significant figures
        else:
            pooled.append(round(np.max(pool), 10))
=======
        pooled.append(round(np.mean(pool), 3)) # can be changed to min, max, or mean; rounded by 3 significant figures
>>>>>>> 3DVisSys/main
        
    return np.array(pooled).reshape(new_shape) # convert to NumpyArray and reshape

# processes geoJSON of maryland area map for Volume plot
def process_map_geojson():
<<<<<<< HEAD
    states = ['maryland-counties.geojson', 
    'Pennsylvania_County_Boundaries.geojson', 
    'Virginia_Counties_Generalized.geojson',
    'de_boundaries_county_state.min.json',
    'WV_County_Boundaries.geojson'
    ]
    colors = ['black',
    '#414141',
    '#00297B',
    '#8E4f3E',
    '#06884F'
    ]

    pts = []
    filtered_pts = []
    colors_list = []
    filtered_colors = []

    for i, state in enumerate(states):
        with open(state, 'r') as file:
            jdata = json.load(file)

        color = colors[i]
        
        for feature in jdata['features']:
            if feature['geometry']['type'] == 'Polygon':
                pts.extend(feature['geometry']['coordinates'][0])    
                for _ in feature['geometry']['coordinates'][0]:
                    colors_list.append(color)
                pts.append([None, None])#mark the end of a polygon   
                colors_list.append("black")
                
            elif feature['geometry']['type'] == 'MultiPolygon':
                for polyg in feature['geometry']['coordinates']:
                    pts.extend(polyg[0])
                    for _ in polyg[0]:
                        colors_list.append(color)
                    pts.append([None, None])#end of polygon
                    colors_list.append("black")                    
            elif feature['geometry']['type'] == 'LineString': 
                pts.extend(feature['geometry']['coordinates'])
                for _ in feature['geometry']['coordinates']:
                    colors_list.append(color)
                pts.append([None, None])
                colors_list.append("black")
    
    for i, pt in enumerate(pts):
        y, x = pt[0], pt[1]
        if (x is None and y is None) or (-80 <= y <= 75 and 37 <= x <= 40):
            filtered_pts.append(pt) 
            filtered_colors.append(colors_list[i])

    y, x = zip(*filtered_pts)    
    z = 0 * np.ones(len(x))

    return x, y, z, filtered_colors
=======
    map_url = "https://raw.githubusercontent.com/frankrowe/maryland-geojson/master/maryland-regions.geojson"

    with urllib.request.urlopen(map_url) as url:
        jdata = json.loads(url.read().decode())

    pts = []

    for feature in jdata['features']:
        if feature['geometry']['type'] == 'Polygon':
            pts.extend(feature['geometry']['coordinates'][0])    
            pts.append([None, None])#mark the end of a polygon   
            
        elif feature['geometry']['type'] == 'MultiPolygon':
            for polyg in feature['geometry']['coordinates']:
                pts.extend(polyg[0])
                pts.append([None, None])#end of polygon
        elif feature['geometry']['type'] == 'LineString': 
            points.extend(feature['geometry']['coordinates'])
            points.append([None, None])
    y, x = zip(*pts)    
    z = 0 * np.ones(len(x))

    return x, y, z
>>>>>>> 3DVisSys/main

def get_locations(lats, lons):
    global locations

    locs = []
    shape = lats.shape
    lats = lats.flatten()
    lons = lons.flatten()

    # locations_rounded contains JSON file with location data rounded to make grabbing data easier
    with open('/home/lanceu/server/locations_rounded.json', 'r') as file:
        locations = json.load(file)

    # grab county data from each coordinate in flattened 2D array
    for i in range(len(lats)):
        try:
            loc = locations[str(lats[i])][str(lons[i])]['county']
            locs.append(loc)
        except:
            locs.append("")

    return np.reshape(locs, shape)

def download_location(i, coord):
    global locations

    lat = coord[0]
    lon = coord[1]
    url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en&zoom=10'

    # ping OpenStreetMap API for lat and lon coordinates and get location data    
    try:
        result = requests.get(url=url)
        result_json = result.json()
        location = result_json['address']
    except:
        location = None

    print(f"\nIteration {i}: Processed lat {lat} and lon {lon} as {location} from \n{url}")
    
    # make nested dictionary first if not already there
    if lat not in locations:
        locations[lat] = {}
    if lon not in locations[lat]:
        locations[lat][lon] = location

    time.sleep(5) # don't spam API and get banned

<<<<<<< HEAD
# function taken from the plotly documentation; converts matplotlib colormaps to plotly colorscales
def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale

def elevation_map():
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

=======
>>>>>>> 3DVisSys/main
# grabs location data from OpenStreetMap for all latitude/longitude coordinates in pooled data
def download_locations():
    global locations

    grb = pygrib.open(file_location + file_name + "00.50" + file_extension)
    data, lats, lons = grb[1].data(lat1=37, lat2=40, lon1=-80+360, lon2=-75+360)
    lons -= 360 # needed as pygrib works with different lon scaling

    pooled_lats = pool_array(lats, 5, 5)
    pooled_lons = pool_array(lons, 5, 5)
    coords = list(zip(pooled_lats.flatten(), pooled_lons.flatten()))

    # locations.JSON contains raw OpenStreetMap API data
    file_path = "/home/lanceu/server/data/locations.json"

    for i, coord in enumerate(coords):
        download_location(i, coord)

        # save periodically in case of crash
        if i % 600 == 0:
            with open(file_path, "w") as json_file:
                json.dump(locations, json_file)
    
    with open(file_path, "w") as json_file:
        json.dump(locations, json_file)

# used to recreate locations file with a set significant figures
def fix_locations():
    f = open("/home/lanceu/server/data/locations.json")
    data = json.load(f)

    new_locations = {}

    # takes raw locations.JSON data and converts into new JSON with rounded locations
    for lat_key in data.keys():
        if lat_key not in new_locations:
            new_lat_key = str(round(float(lat_key), 3))
            new_locations[new_lat_key] = {}

        for lon_key in data[lat_key].keys():
            if lon_key not in new_locations[new_lat_key]:
                new_lon_key = str(round(float(lon_key), 3))
                new_locations[new_lat_key][new_lon_key] = data[lat_key][lon_key]

    with open("/home/lanceu/server/data/locations_test.json", "w") as json_file:
        json.dump(new_locations, json_file)

    print(new_locations)
    
if __name__ == '__main__':
<<<<<<< HEAD
    _, ocean_map = elevation_map()
    fig = go.Figure(data = [ocean_map])
    fig.show()
=======
    fix_locations()
>>>>>>> 3DVisSys/main
