from multiprocessing import Pool
from geopy.geocoders import Nominatim
import numpy as np
import pygrib, time, json, urllib, requests

start_time = time.time()
locations = {}

file_location = '/home/lanceu/server/testdata/SampleData/'
file_name = 'MRMS_MergedReflectivityQC_'
file_extension = "_20210708-120040" +'.grib2'
height = "00.50" # any height will work for location data

# takes large arrays and creates smaller array of 5x5 means of original
def pool_array(data, pool_size, stride):
    pools = []
    pooled = []

    for i in np.arange(data.shape[0], step=stride):
        for j in np.arange(data.shape[1], step=stride):
            pool = data[i:i+pool_size, j:j+pool_size]
            pools.append(pool) # array of pools prior to mean/min/maxing
    
    new_shape = (int(data.shape[0] / pool_size), int(data.shape[1] / pool_size)) 

    for pool in pools: # make new pooled array as Python array first to append first
        pooled.append(round(np.mean(pool), 3)) # can be changed to min, max, or mean; rounded by 3 significant figures
        
    return np.array(pooled).reshape(new_shape) # convert to NumpyArray and reshape

# processes geoJSON of maryland area map for Volume plot
def process_map_geojson():
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
    fix_locations()
