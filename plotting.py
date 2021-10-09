import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import station

# see Python routine "parse-csv.py" for the method of filtering data and making these csv files
GIPY05 = pd.read_csv("./data/GIPY05_filtered.csv")
GIPY04 = pd.read_csv("./data/GIPY04_filtered.csv")
GA03 = pd.read_csv("./data/GA03_filtered.csv")
GP02 = pd.read_csv("./data/GP02_filtered.csv")
GIPY0405 = pd.concat([GIPY04, GIPY05], ignore_index=True) #merging the csv files for GIPY04 and GIPY05


###SUBPLOTS PLOTTING

def get_x_y_values(cruise, lat, lon, data_name):
    #getting the x and y values to plot the depth profile for a given parameter (data_name) at a given lat and lon
    if cruise == 'GIPY0405':
        xvals = GIPY0405[data_name][(GIPY0405['Latitude'] == lat) & (GIPY0405['Longitude'] == lon)]
        yvals = GIPY0405['Depth'][(GIPY0405['Latitude'] == lat ) & (GIPY0405['Longitude'] == lon)]
    elif cruise == 'GA03':
        xvals = GA03[data_name][(GA03['Latitude'] == lat) & (GA03['Longitude'] == lon)]
        yvals = GA03['Depth'][(GA03['Latitude'] == lat) & (GA03['Longitude'] == lon)]
    elif cruise == 'GP02':
        xvals = GP02[data_name][(GP02['Latitude'] == lat) & (GP02['Longitude'] == lon)]
        yvals = GP02['Depth'][(GP02['Latitude'] == lat) & (GP02['Longitude'] == lon)]
    return [xvals, yvals]


def update_legend(fig, cruise, hov_station, click_stations):
    if station.is_empty(hov_station) == False:
        fig['data'][0]['showlegend'] = True
        fig['data'][0]['name'] = str(hov_station.name) + '<br>lat: ' + str("{:.2f}".format(hov_station.lat)) \
                                 + '<br>lon: ' + str("{:.2f}".format(hov_station.lon))
    if (len(click_stations) != 0):
        for i in range(len(click_stations)):
            fig['data'][i+1]['showlegend'] = True
            for i in range(len(click_stations)):
                fig['data'][i+1]['name'] = str(click_stations[i].name) + '<br>lat: ' + str("{:.2f}".format(click_stations[i].lat)) \
                                         + '<br>lon: ' + str("{:.2f}".format(click_stations[i].lon))
    if cruise == 'GIPY0405':
        fig.update_layout(legend_title_text='<b>' + 'GIPY04 & GIPY05' + '</b>' + '<br></br>Selected Stations:')
    else:
        fig.update_layout(legend_title_text='<b>' + str(cruise) + '</b>' + '<br></br>Selected Stations:')
    return fig


#initialize the profiles
def initialize_profiles(cruise):
    fig = px.scatter(x=[None], y=[None])
    # empty traces for hovered data
    figT = px.scatter(x=[None], y=[None], color_discrete_sequence=['blue'])
    fig.add_trace(figT.data[0])

    for i in range(8):
        #traces for clicked data
        figT = px.scatter(x=[None], y=[None])
        fig.add_trace(figT.data[0])
    fig.update_xaxes(range=[-5, 30])
    return fig



def switch_profiles(cruise, fig):
    for i in range(9):
        fig.data[i].update(x=[None], y=[None])
        fig['data'][i].visible = False
    return fig

def update_profiles(hov_station, click_stations, cruise, fig):

    if station.is_empty(hov_station) == False:
        fig.data[0].visible = True
        hov_xvals_temp, hov_yvals_temp = get_x_y_values(cruise, hov_station.lat, hov_station.lon, 'Temperature')
        fig.data[0].update(x=hov_xvals_temp, y=hov_yvals_temp)

    else:
        fig.data[0].update(x=[None], y=[None])
        fig.data[0].visible = False

    if len(click_stations) != 0:
        for i in range(8):
            if i < len(click_stations):
                fig.data[i + 1].visible = True
                click_xvals_temp, click_yvals_temp = get_x_y_values(cruise, click_stations[i].lat, click_stations[i].lon, 'Temperature')
                fig.data[i+1].update(x=click_xvals_temp, y=click_yvals_temp, marker_color=click_stations[i].colour)
            else:
                fig.data[i+1].update(x=[None], y=[None])
                fig.data[i+1].visible = False

    #display cruise info
    fig = update_legend(fig, cruise, hov_station, click_stations)
    fig.update_xaxes(range=[-5, 30])
    return fig


###MAP PLOTTING

def plot_stations(cruise, click_stations):
    if cruise == 'GIPY0405':
        fig = px.scatter_mapbox(GIPY0405, lat="Latitude", lon="Longitude", hover_name="Station",
                                color_discrete_sequence=['blue'], zoom=1.2, center=dict(lat=-50, lon=0))
    elif cruise == 'GA03':
        fig = px.scatter_mapbox(GA03, lat="Latitude", lon="Longitude", hover_name="Station",
                                color_discrete_sequence=['blue'],
                                zoom=1.2)
    elif cruise == 'GP02':
        fig = px.scatter_mapbox(GP02, lat="Latitude", lon="Longitude", hover_name="Station",
                                color_discrete_sequence=['blue'],
                                zoom=1.2)
    fig.update_layout(mapbox_style="open-street-map")


    # adding markers from: https://plotly.com/python/scattermapbox/
    if (len(click_stations) != 0):
        for i in range(len(click_stations)):
            fig.add_trace(go.Scattermapbox(lat=[click_stations[i].lat], lon=[click_stations[i].lon], showlegend=False,
                                           hovertemplate="<b>" + str(click_stations[i].name) +
                                                         "</b><br><br>Latitude=%{lat} </br> Longitude=%{lon}<extra></extra>",
                                           mode='markers', marker=go.scattermapbox.Marker(size=10, color=click_stations[i].colour)))

    return fig

#figure functions
def initialize_map(cruise):

    fig = plot_stations(cruise, []) #***

    if cruise == 'GIPY0405':
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title='GIPY04 and GIPY05')
    else:
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title=cruise)

    return fig

# update map for cruise changes
def switch_map(cruise, fig):
    fig.data = []
    fig = plot_stations(cruise, [])

    if cruise == 'GIPY0405':
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title='GIPY04 and GIPY05')
    else:
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title=cruise)

    return fig


def update_map(click_stations, figure_data, cruise):

    fig = plot_stations(cruise, click_stations)
    if figure_data is not None: #set map layout to its previous settings, so the zoom and position doesn't reset
        fig.layout['mapbox'] = figure_data['layout']['mapbox']

    if cruise == 'GIPY0405':
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title='GIPY04 and GIPY05')
    else:
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, title=cruise)
    return fig