import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
from plotly.graph_objs._figure import Figure


WEEKDAYS={0:"Mon", 1:"Tu", 2:"Wed", 3:"Thu", 4:"Fri", 5:"Sat", 6:"Sun"}

COUNTRY_LINE_COLOUR="#2cfec1"
FLIGHT_LINE_COLOUR = '#9467bd'

states_geojson = requests.get(
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_1_states_provinces_lines.geojson"
).json()

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

def default_empty_fig() -> Figure:
    """ Provides a placeholder figure for when there's no flight data """
    fig = px.bar(x=[0, 0], y= ['Avg', '-']
                 ).update_layout(xaxis_title="No Data", yaxis_visible=False,
                                margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='#252e3f')
    return fig


def default_flight_fig() -> Figure:
    """ Provides a placeholder flight map for when there's no flight data """
    fig = px.scatter_geo(pd.DataFrame(data={'lat': [], 'long': []}), lat='lat', lon='long', projection='orthographic'
                         ).update_layout(plot_bgcolor='#252e3f', 
                                         margin=dict(l=20, r=20, t=20, b=20))
    fig = add_state_lines(fig)
    fig.update_geos(
        visible=True, resolution=50, scope="world", showcountries=True, 
        countrycolor=COUNTRY_LINE_COLOUR)
    return fig

def num_of_flights_over_time(flights: dict[dict]) -> Figure:
    """ Creates a graph of which days the fly on the most """
    if flights["fuel_usage"] == {}:
        return default_empty_fig()

    list_of_days = []
    
    flight_data = pd.DataFrame.from_dict(flights) 
    flight_data = flight_data.drop_duplicates()
    flight_data["day"] = pd.to_datetime(flight_data['dep_time']).apply(lambda x: WEEKDAYS[x.weekday()])

    flight_data = flight_data.groupby('day').count().reset_index()
    
    fig = px.bar(flight_data, x='day').update_layout(xaxis_title="Day of Week",yaxis_title="Number of Flights",
                                margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='#252e3f')

    return fig

def co2_flight_vs_avg(flight_data:dict, avg_co2:float) -> Figure:
    """ Produces figure contrasting the co2 output of 
        the previous flight to the daily average """
    celeb_name = flight_data["owner"]
    flight_co2 = flight_data["co2"]

    fig = px.bar(x=[avg_co2, flight_co2], y= ['Avg', "Celeb"]
                 ).update_layout(xaxis_title="CO2 vs Avg Yr CO2 per 1000 people", yaxis_title=None,
                                margin=dict(l=20, r=20, t=20, b=20), 
                                 plot_bgcolor='#252e3f')
    return fig

def cost_flight_vs_avg(flight_data:dict, avg_wage:float) -> Figure:
    """ Produces figure contrasting the co2 output of 
        the previous flight to the daily average """
    celeb_name = flight_data["owner"]
    flight_cost = flight_data["cost"]
    wage_cost = flight_data["time"] * avg_wage

    fig = px.bar(x=[wage_cost, flight_cost], y= ['Avg', "Celeb"]
                 ).update_layout(xaxis_title="100 Median Wages (during flight) vs Cost",yaxis_title=None,
                                margin=dict(l=20, r=20, t=20, b=20),plot_bgcolor='#252e3f')
    return fig


def create_flight_map(flight: dict) -> Figure:
    """ Uses lat/lon of departure/arrival airports to plot a flight path of a celeb """
    midpoint = [(flight['lat'][1] - flight['lat'][0])/2 + flight['lat'][0], (flight['long'][1] - flight['long'][0])/2+ flight['long'][0]]
    df = pd.DataFrame(data=flight)

    fig = px.scatter_geo(df, lat='lat', lon='long', projection='orthographic'
                         ).update_layout(plot_bgcolor='#252e3f', 
                                         margin=dict(l=20, r=20, t=20, b=20))
    fig = add_state_lines(fig)
    fig = add_flight_trace(fig, flight)

    fig.update_geos(
        visible=True, resolution=50, scope="world", showcountries=True, 
        countrycolor=COUNTRY_LINE_COLOUR, projection_rotation = {'lat': midpoint[0], 'lon': midpoint[1], 'roll': 0})
    return fig

def add_flight_trace(fig: Figure, data: dict):
    fig.add_trace(
        go.Scattergeo(lat=data['lat'], lon=data['long'], line_color=FLIGHT_LINE_COLOUR,
                      line_width=3, mode="lines", showlegend=False))
    return fig

def add_state_lines(fig: Figure) -> Figure:
    """ This code gets the state lines data, and adds to figure """
    fig = fig.add_trace(
        go.Scattergeo(
            lat=[v for sub in [
                    np.array(f["geometry"]["coordinates"])[:, 1].tolist() + [None]
                    for f in states_geojson["features"]
                ] for v in sub],
            lon=[v for sub in [
                    np.array(f["geometry"]["coordinates"])[:, 0].tolist() + [None]
                    for f in states_geojson["features"]] for v in sub
            ],
            line_color=COUNTRY_LINE_COLOUR,
            line_width=1,
            mode="lines",
            showlegend=False,
            opacity=0.4
        )
    )
    return fig