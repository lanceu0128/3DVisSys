import requets

start_time = time.time()
locations = {}

file_location = '/home/lanceu/server/testdata/SampleData/'
file_name = 'MRMS_MergedReflectivityQC_'
file_extension = "_20210708-120040" +'.grib2'
height = "00.50" # any height will work for location data

def download_location(i, coord):
    '''
    Helper function for download_locations(). Pings the OSM API for a location given coordinates.

    Note that this isn't used in any automated process.
    '''

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

def download_locations():
    '''
    Grabs location data from OpenStreetMap for all latitude/longitude coordinates in pooled data

    Note that this isn't used in any automated process.
    '''

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

def fix_locations():
    '''
    Used to recreate locations file with 3 significant figures. 

    Note that this isn't used in any automated process.
    '''
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

    with open("/home/lanceu/server/data/locations_rounded.json", "w") as json_file:
        json.dump(new_locations, json_file)

    print(new_locations)
    
if __name__ == '__main__':
    download_locations()