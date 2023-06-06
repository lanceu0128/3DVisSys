import pygrib
import plotly.graph_objects as go
import numpy as np

file = pygrib.open("MRMS_PrecipRate.latest.grib2")
# file = pygrib.open("MRMS_PrecipRate_00.00_20230605-165800.grib2")

file.seek(0)

for grb in file:
    print(grb)
    print(grb.keys())

    data, lats, lons = grb.data(lat1=20, lat2=70, lon1=220, lon2=320)

    lats_graph = []
    lons_graph = []

    for i in range(len(lats)):
        if (i % 20 == 0):
            lats_graph.append(lats[i])
            lons_graph.append(lons[i])

print(len(lats_graph))
    

# fig = go.Figure(data=[go.Scatter3d(
#     x = lons,
#     y = lats,
#     z = [1 for i in range(len(lons))],
#     mode = "markers"
# )])
# fig.show()