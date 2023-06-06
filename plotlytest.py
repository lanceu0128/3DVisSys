import plotly.graph_objects as go
import plotly.data as data
import numpy as np
import pandas as pd
import pprint

x1 = np.linspace(1, 10, 11)
y1 = np.linspace(1, 10, 11)
z1 = np.linspace(1, 10, 11)

X, Y, Z = np.meshgrid(x1, y1, z1)
values = np.sin(np.pi*X) * np.cos(np.pi*Z) * np.sin(np.pi*Y)

print(values)

fig = go.Figure(data = go.Volume(
    x = X.flatten(),
    y = Y.flatten(),
    z = Z.flatten(),
    value = values.flatten(),
    isomin=-0.1,
    isomax=0.8,
    opacity=0.1, # needs to be small to see through all surfaces
))

fig.show()