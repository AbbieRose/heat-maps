import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
from flask import Flask

import pandas as pd
import numpy as np
import math

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

file = "data/7542.json"

data = pd.read_json(file)

meta_columns = ["player","team"]
metadata = data[meta_columns]
metadata = (metadata[metadata.player.notnull()])
metadata["player"] = pd.DataFrame(metadata["player"].to_list())["name"]
metadata["team"] = pd.DataFrame(metadata["team"].to_list())["name"]
metadata = (metadata[metadata.player.notnull()])
metadata = (metadata[metadata.team.notnull()])
metadata = metadata.drop_duplicates()
meta_dict = []
for index, row in metadata.iterrows() :
    meta_dict.append({"label":row['player'], "value":row['player']})
print(meta_dict)


event_columns = ["player","type","timestamp","location"]
events = (data[data.location.notnull()])[event_columns]

events["player"] = pd.DataFrame(events["player"].to_list())["name"]
events["type"] = pd.DataFrame(events["type"].to_list())["name"]

events["loc_x"] = pd.DataFrame(events["location"].to_list())[0]
events["loc_y"] = pd.DataFrame(events["location"].to_list())[1]

events = (events[events.player.notnull()])

initial_player = "Mbark Boussoufa"
init_events = events[events["player"] == initial_player]
init_events["location"].to_list()

# player picker, file picker
# then the next thing I want is a bucket adjustor
# and a smoother
fig = px.density_heatmap(init_events, x="loc_x", y="loc_y", nbinsx=30, nbinsy=20, color_continuous_scale="Viridis")

test_options= [
    {"label": "Boussoufa", "value": "Mbark Boussoufa"},
    {"label": "Another", "value": "Another Player"}
]

app.layout = html.Div(children=[
    html.H1('Pick a player to see their heatmap'),
    dcc.Dropdown(
        id="players",
        options=meta_dict
    ),
    dcc.Graph(id="heatmap", figure=fig),
    html.H3('Slide to choose a bin size'),
    dcc.Slider(
        id='bin-slider',
        min=1,
        max=10,
        step=1,
        value=1
    )
])

@app.callback(
    dash.dependencies.Output("heatmap", "figure"),
    [dash.dependencies.Input ("players", "value"),
     dash.dependencies.Input("bin-slider","value")])
def update_graph(player, value) :
    newxbins = math.floor(120 / value)
    newybins = math.floor(80 / value)
    print(newxbins)
    print(newybins)
    player_events = events[events["player"] == player]
    player_events["location"].to_list()
    return px.density_heatmap(player_events, x="loc_x", y="loc_y", nbinsx=newxbins, nbinsy=newybins, color_continuous_scale="Viridis")

if __name__ == '__main__' :
    app.run_server()
