# -*- coding: utf-8 -*-

# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/
# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# mouse-over or 'hover' behavior is based on https://dash.plotly.com/interactive-graphing
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line
# Mapmaking code initially learned from https://plotly.com/python/mapbox-layers/.


from flask import Flask
from os import environ
import json

import dash
from dash import dcc
from dash import html
#import dash_core_components as dcc
#import dash_html_components as html
from dash.dependencies import Input, Output

import plotting as plot
import station

#initial settings for the plots
initial_cruise = 'GIPY0405'
#initial_hov_station = station.Station('hover', None, None, None, 'blue')
#initial_click_stations = []

def station_dict(obj):
    return obj.__dict__

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(__name__,server=server,
                external_stylesheets=external_stylesheets)

app.layout = html.Div([

# This is the plot with the map of cruise stations
    html.Div([
        dcc.Graph(
            id='map',
            config={
                'staticPlot': False,  # True, False
                'scrollZoom': True,  # True, False
                'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                'showTips': True,  # True, False
                'displayModeBar': False,  # True, False, 'hover'
                'watermark': True,
                'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d'],
            },
            clear_on_unhover = True, #clears hover plots when cursor isn't over the station
        )
    ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),


    # slider or checklist details at https://dash.plotly.com/dash-core-components
    # checkboxes can be lumped together but then logic in "update_graph" is messier.
    # Content can be delivered using html, but markdown is simpler.
    html.Div([

        # choose the cruise
        dcc.Markdown('''
        **Select Cruise**
        '''),

        dcc.RadioItems( #radiobuttons to choose the current cruise
            id='cruise',
            options=[
                {'label': 'GIPY04 and GIPY05', 'value': 'GIPY0405'},
                {'label': 'GA03', 'value': 'GA03'},
                {'label': 'GP02', 'value': 'GP02'}
            ],
            value=initial_cruise,
            style={"margin-bottom": "30px"}
        ),

        # button to clear the selected stations from the map
        #html.Button('Clear', id='clear_button', style={'margin-top': '30px'})

    ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'middle'}),

    html.Div([
        # the graph of subplots which show depth profiles for different parameters
        dcc.Graph(
            id='profiles',
            config={
                'staticPlot': False,  # True, False
                'scrollZoom': False,  # True, False
                'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                'showTips': True,  # True, False
                'displayModeBar': 'hover',  # True, False, 'hover'
                'watermark': False,
                'modeBarButtonsToRemove': ['resetAxis', 'pan2d', 'resetScale2d', 'select2d', 'lasso2d', 'zoom2d',
                                           'zoomIn2d', 'zoomOut2d', 'hoverCompareCartesian', 'hoverClosestCartesian',
                                           'autoScale2d'],
            }
        ),
    ], style={'display': 'inline-block', 'width': '93%', 'vertical-align': 'middle', 'margin-bottom': '50px'}),

    # Using dcc.Store (https://dash.plotly.com/dash-core-components/store) to store values of the hover station and the clicked stations
    # The hov_station is the station currently being hovered over by the mouse. clicked_stations is a list of stations
    # that were clicked and should be plotted. dcc.Store stores a variable as a json, and then it can be accessed through a callback.
    #dcc.Store(id='hov_station', data=json.dumps(station.Station('hover', None, None, None, 'blue').__dict__), storage_type='memory'),
    #dcc.Store(id='click_stations', data=json.dumps([], default=station_dict), storage_type='memory'),
    dcc.Store(id='hov_station', data={}, storage_type='memory'),
    dcc.Store(id='click_stations', data={}, storage_type='memory'),
], style={'width': '1000px'})


#initialize the map and the depth profiles. Plotted through the 'plotting' file.
#fig_map = plot.initialize_map(initial_cruise) #fig_map is the figure with the map of the stations
#fig_profiles = plot.initialize_profiles(initial_cruise) #fig_profiles is the figure with depth profile subplots

#update the hover station
@app.callback(
    Output(component_id='hov_station', component_property='data'), # we output a json to the dcc.Store variable 'hov_station'
    Input(component_id='map', component_property='hoverData'), #the hover data from the map, which tells us which station the mouse is hovering over
    Input(component_id='cruise', component_property='value'),
    Input(component_id='hov_station', component_property='data'),
)
def update_hover_station(hov_data, cruise, hov_station_json):
    #the right statement checks if the cruise was just switched. If the cruise is switched, we clear the hover.
    if (hov_station_json == {}) | (hov_station_json == None) | (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        #clear hover
        hov_station = station.Station('hover', None, None, None, 'blue') #empty station
    else:
        hov_station = station.get_hov_station(hov_data)

    return json.dumps(hov_station.__dict__) #return a json dict of the station to be stored

'''
# The clear button callback. Uses the dcc.Store 'clear_data' property to clear the stored information.
@app.callback(
    Output(component_id='click_stations', component_property='clear_data'),
    Output(component_id='hov_station', component_property='clear_data'),
    Input(component_id='clear_button', component_property='n_clicks'),
)
def clear_stations(n_clicks):
    return True, True
'''


# The callback for the 'clicked_stations' list. We input the current stored value for clicked_stations, update it, and return it.
@app.callback(
    Output(component_id='click_stations', component_property='data'),
    Input(component_id='map', component_property='clickData'),
    Input(component_id='click_stations', component_property='data'),
    Input(component_id='cruise', component_property='value'),
)
def update_click_stations(click_data, click_stations_json, cruise):
    #converting the inputed clicked_stations to a list of Station objects from a json.
    if (click_stations_json == None) | (click_stations_json == {}):
        click_stations = []
    else:
        click_stations = station.dict_list_to_station(json.loads(click_stations_json))

    #if the cruise was just switched, we clear the clicked stations list
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        click_stations = []
    #if the click_data was just updated, we add the new clicked station to the list. The
    # if statement prevents adding the same station multiple times, as click_data doesn't clear.
    elif (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'map'):
        click_stations = station.get_click_stations(click_data, click_stations)

    return json.dumps(click_stations, default=station_dict) #convert to json and return clicked_stations

#Depth profiles
@app.callback(
    Output(component_id='profiles', component_property='figure'),
    Input(component_id='profiles', component_property='figure'),
    Input(component_id='hov_station', component_property='data'),
    Input(component_id='click_stations', component_property='data'),
    Input(component_id='cruise', component_property='value'),
)
def update_profiles(fig_profiles, hov_station_json, click_stations_json, cruise):
    if fig_profiles == None:
        fig_profiles = plot.initialize_profiles(initial_cruise) #fig_profiles is the figure with depth profile subplots

    #read in the jsons for hov_station and click_stations
    hov_station = station.dict_to_station(json.loads(hov_station_json))
    click_stations = station.dict_list_to_station(json.loads(click_stations_json))

    # if the callback that was triggered was the cruise changing, we switch profiles (switch cruises)
    # otherwise, we update the profiles for the current cruise
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        fig = plot.switch_profiles(cruise, fig_profiles)
    else:
        fig = plot.update_profiles(hov_station, click_stations, cruise, fig_profiles)
    return fig



# Callback for the map plot
@app.callback(
    Output(component_id='map', component_property='figure'),
    Input(component_id='map', component_property='figure'),
    Input(component_id='cruise', component_property='value'),
    Input(component_id='click_stations', component_property='data'),
    Input(component_id='map', component_property='figure')
)
def update_map(fig_map, cruise, click_stations_json, figure_data):
    if fig_map == None:
        fig_map = plot.initialize_map(initial_cruise) #fig_profiles is the figure with depth profile subplots
    #read in the click_stations json
    click_stations = station.dict_list_to_station(json.loads(click_stations_json))
    # switch map is called when we switch cruises, update map is called for other updates.
    if (dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'cruise'):
        fig = plot.switch_map(cruise, fig_map)
    else:
        fig = plot.update_map(click_stations, figure_data, cruise)
    return fig



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
