import gzip, shutil

file_extension = ".grib2.gz"
file_location = 'testdata/SampleData/'
file_name = 'MRMS_MergedReflectivityQC_'
file_date = '_20210708-120040'
heights = ["00.50", "00.75", "01.00", "01.25", "01.50", "01.75", "02.00", "02.25", "02.50", "02.75", "03.00", "03.50", "04.00", "04.50", "05.00", "05.50", "06.00", "06.50", "07.00", "07.50", "08.00", "08.50", "09.00", "10.00", "11.00", "12.00", "13.00", "14.00", "15.00", "16.00", "17.00", "18.00", "19.00"]

for height in heights:
    location = file_location + file_name + height + file_date + file_extension
    unzip_location = location.replace(".gz", "")

    with gzip.open(location, 'rb') as infile:
        with open(unzip_location, 'wb') as outfile:
            shutil.copyfileobj(infile, outfile)