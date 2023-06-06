from flask import Flask
import requests
import gzip, shutil

app = Flask(__name__)
latest_data_url = "https://mrms.ncep.noaa.gov/data/2D/PrecipRate/MRMS_PrecipRate.latest.grib2.gz"
file_location = 'data/MRMS_PrecipRate.latest.grib2.gz'

@app.route('/')
def main():
    return 'Hello World'

@app.route('/download/latest')
def download():
    r = requests.get(latest_data_url, allow_redirects=True)
    open(file_location, 'wb').write(r.content)

    with gzip.open(file_location, 'rb') as infile:
        with open('data/MRMS_PrecipRate.latest.grib2', 'wb') as outfile:
            shutil.copyfileobj(infile, outfile)

    return "Downloading File"

@app.route('/hello/<name>')
def hello(name):
    return (f'Hello {name}!')

if __name__ == '__main__':
    app.run()