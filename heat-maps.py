import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
from flask import Flask

import os
import pandas as pd
import numpy as np
import math
from sklearn.decomposition import NMF

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# load all games
raw_data = pd.read_json("data/matches.json")

games_dict = []
game_columns = ["match_id", "home_team", "away_team", "home_score", "away_score", "competition_stage"]
games = raw_data[game_columns]
games["home_team"] = pd.DataFrame(games["home_team"].to_list())["home_team_name"]
games["away_team"] = pd.DataFrame(games["away_team"].to_list())["away_team_name"]
for index, row in games.iterrows() :
    print(row['home_team'])
    display_string = row['home_team'] + " " + str(row['home_score']) + " - " + str(row['away_score']) + " " + row['away_team']
    games_dict.append({"label":display_string, "value": row['match_id'] })

print(games_dict)

# there's a bug in the mexico sweden game I think
def load_one_game(file) :
    print("Loading one game from file: ")
    print(file)
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

    event_columns = ["player","type","timestamp","location"]
    events = (data[data.location.notnull()])[event_columns]
    events = events.dropna()
    
    events["player"] = pd.DataFrame(events["player"].to_list())["name"]
    events["type"] = pd.DataFrame(events["type"].to_list())["name"]

    events["loc_x"] = pd.DataFrame(events["location"].to_list())[0]
    events["loc_y"] = pd.DataFrame(events["location"].to_list())[1]

    events = (events[events.player.notnull()])
    return meta_dict, events

def factorHeatmap(x, y, components) :
    field_matrix = np.zeros(shape=(120,80))
    locations = zip(x,y)
    
    for loc in locations :
        x_pos = int(loc[0])
        y_pos = int(loc[1])
        field_matrix[x_pos][y_pos] = field_matrix[x_pos][y_pos] + 1
    
    model = NMF(n_components=components, init='random', random_state=0)
    W = model.fit_transform(field_matrix)
    H = model.components_

    factor_matrices = []
    for c in range(components) :
        w_vec = W[:,c]
        h_vec = H[c]

        temp_map = np.matmul(w_vec[:,None], np.matrix.transpose(h_vec[:,None])) 
        temp_fig = px.imshow(np.matrix.transpose(temp_map))
        factor_matrices.append(temp_fig)
    return factor_matrices

# add a smoother
#factor_matrices = factorHeatmap(init_events["loc_x"], init_events["loc_y"], 3)
# Hirving Rodrigo Lozano Bahena
def populate_initial_game() :
    file = "data/7566.json"
    init_player = "Hirving Rodrigo Lozano Bahena"
    init_metadata, init_events = load_one_game(file)
    player_events = init_events[init_events["player"] == init_player]
    #player_events["location"].to_list()
    return player_events, init_metadata

init_events, init_meta = populate_initial_game()
print(init_meta)

fig = px.density_heatmap(init_events, x="loc_x", y="loc_y", nbinsx=30, nbinsy=20, color_continuous_scale="Viridis")

test_options= [
    {"label": "Boussoufa", "value": "Mbark Boussoufa"},
    {"label": "Another", "value": "Another Player"}
]

app.layout = html.Div(children=[
    html.H1('First, choose a game.'),
    dcc.Dropdown(
        id="games",
        options=games_dict
    ),
    html.H1('Next, choose a player to see their heatmap in that game.'),
    dcc.Dropdown(
        id="players",
        options=init_meta
    ),
    dcc.Graph(id="heatmap", figure=fig),
    html.H3('Slide to choose a bin size'),
    dcc.Slider(
        id='bin-slider',
        min=1,
        max=10,
        step=1,
        value=1
    ),
    html.Div(id='event-data', style={'display':'none'})
])

# can I not just set the new dropdown directly?
@app.callback(
    [dash.dependencies.Output('players', 'options'),
     dash.dependencies.Output('event-data', 'children')],
    [dash.dependencies.Input('games','value')])
def choose_game(game) :
    file_name = "data/" + str(game) + ".json"
    metadata, event_data = load_one_game(file_name)

    return metadata, event_data.to_json(date_format='iso', orient='split')

# may eventually want to split these out
@app.callback(
    dash.dependencies.Output("heatmap", "figure"),
    [dash.dependencies.Input("event-data", "children"),
     dash.dependencies.Input("players", "value"),
     dash.dependencies.Input("bin-slider","value")])
def update_graph(events_json, player, value) :
    if player :
        events = pd.read_json(events_json, orient='split')
        player_events = events[events["player"] == player]
        
        newxbins = math.floor(120 / value)
        newybins = math.floor(80 / value)
        print("loc_x: ")
        print(player_events["loc_x"])
        
        return px.density_heatmap(player_events, x="loc_x", y="loc_y", nbinsx=newxbins, nbinsy=newybins, color_continuous_scale="Viridis")
    else :
        return {}
    
if __name__ == '__main__' :
    app.run_server()
