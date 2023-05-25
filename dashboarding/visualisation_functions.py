import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
from pandas import DataFrame
from plotly.graph_objs._figure import Figure


COUNTRY_LINE_COLOUR="#2cfec1"
FLIGHT_LINE_COLOUR = '#9467bd'

states_geojson = requests.get(
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_1_states_provinces_lines.geojson"
).json()

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

def default_empty_fig() -> Figure:
    """ Provides a placeholder figure for when there's no flight data """
    fig = px.bar(x=[1, 2], y= ['Avg', '-']
                 ).update_layout(xaxis_title="Placeholder graph", yaxis_visible=False,
                                margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='#252e3f')
    return fig


def default_flight_fig() -> Figure:
    """ Provides a placeholder figure for when there's no flight data """
    fig = px.scatter_geo(pd.DataFrame(data={'lat': [], 'long': []}), lat='lat', lon='long', projection='orthographic'
                         ).update_layout(plot_bgcolor='#252e3f', 
                                         margin=dict(l=20, r=20, t=20, b=20))
    fig = add_state_lines(fig)
    return fig


def co2_of_flight_vs_average(flight_data:dict, avg_co2:float) -> Figure:
    """ Produces figure contrasting the co2 output of 
        the previous flight to the daily average """
    celeb_name = flight_data["owner"]
    flight_co2 = flight_data["co2"]

    fig = px.bar(x=[avg_co2, flight_co2], y= ['Avg', celeb_name]
                 ).update_layout(xaxis_title="Flight CO2 vs Avg Yearly CO2 for 1000 people", yaxis_visible=False,
                                margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='#252e3f')
    return fig

def cost_of_flight_vs_average(flight_data:dict, avg_wage:float) -> Figure:
    """ Produces figure contrasting the co2 output of 
        the previous flight to the daily average """
    celeb_name = flight_data["owner"]
    flight_cost = flight_data["cost"]
    wage_cost = flight_data["time"] * avg_wage

    fig = px.bar(x=[wage_cost, flight_cost], y= ['Avg', celeb_name]
                 ).update_layout(xaxis_title="100 Median Wages over flight time vs Flight cost", yaxis_visible=False,
                                margin=dict(l=20, r=20, t=20, b=20),plot_bgcolor='#252e3f')
    return fig

def number_of_flights_over_time() -> Figure:
    """ Produces figure showing number of flights over last 6 mnths """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    flights = [1, 3, 2, 5, 6, 4]
    fig = px.bar(x=months, y=flights).update_layout(
                            xaxis_title="Flights over 6 mnths",
                            yaxis_title="No. of flights",
                            margin=dict(l=20, r=20, t=20, b=20),plot_bgcolor='#252e3f')
    return fig

def create_flight_map(flight: dict) -> Figure:
    print(flight['lat'])
    midpoint = [(flight['lat'][1] - flight['lat'][0])/2, (flight['long'][1] - flight['long'][0])/2]
    df = pd.DataFrame(data=flight)

    fig = px.scatter_geo(df, lat='lat', lon='long', projection='orthographic'
                         ).update_layout(plot_bgcolor='#252e3f', 
                                         margin=dict(l=20, r=20, t=20, b=20))
    fig = add_state_lines(fig)
    fig = add_flight_trace(fig, flight)

    fig.update_geos(
        visible=True, resolution=50, scope="world", showcountries=True, 
        countrycolor=COUNTRY_LINE_COLOUR)
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