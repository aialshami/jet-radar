import pandas as pd
import os
from dash import Dash, html, dcc, page_container, page_registry
from dotenv import load_dotenv
from dash.dependencies import Input, Output, State
from visualisation_functions import co2_of_flight_vs_average, cost_of_flight_vs_average, number_of_flights_over_time, create_flight_map
from db_connections import get_data_as_dataframe, SQLconnection
from conversion_metrics import get_age_from_birthdate
from conversion_metrics import get_celeb_info, get_number_of_flights

from conversion_metrics import get_new_infographic_text

import numpy as np

from conversion_metrics import UNICODE, CELEB_DROPDOWN_OPTIONS

load_dotenv()
TEMP_FLIGHT = {'Location': ['Start', 'End'], 'lat': [30, 40], 'long': [-90, -80]}



app = Dash(__name__, use_pages=False)
app.title = "MuskJet 2.0"
server = app.server

PAST_FLIGHTS = [1, 2, 3, 4, 5, 6]

# Get data
sql_conn = SQLconnection(config=os.environ)
owner_df = get_data_as_dataframe(sql_conn, "owner")
aircraft_df = get_data_as_dataframe(sql_conn, "aircraft")
model_df = get_data_as_dataframe(sql_conn, "model")
flight_df = get_data_as_dataframe(sql_conn, "flight")
gender_df = get_data_as_dataframe(sql_conn, "gender")


# HTML document
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="app-container",
            children=[
                html.Div(id="celeb-column", 
                         children=[
                             html.Img(id='celeb-img', src='assets/celeb_photos/elon_musk.jpg'),
                             html.Div(id="celeb-info", children=[
                                 html.Ul(id='celeb-info-list', children=[
                                    html.Li(id='celeb-info-text-name', children=f"Name: Elon Musk"),
                                    html.Li(id='celeb-info-text-gender', children=f"Gender: Male"),
                                    html.Li(id='celeb-info-text-age', children=f"Age: 51"),
                                    html.Li(id='celeb-info-text-worth', children=f"Worth: 180000 M")]),
                                 ]),
                            html.Div(id="flights-tracked-container", className="container", children=[
                                html.P(id="num-flights-tracked",className="box", children="# of flights tracked is: "),
                            ]),
                        ]),
                html.Div(id="center-column",
                         children=[
                             html.H4(id="title", children="Visualisation of private jet emissions & costs"),
                             html.P(id="description", children="Climate Change is a fundamental political issue, with \
                                                                75%% of adults in Britain at least somewhat worried about the climate. \
                                                                It can be difficult to understand the impact that a small set of people \
                                                                have compared to the rest of us - this tool aims to fix that."),
                             dcc.Dropdown(
                                        options=CELEB_DROPDOWN_OPTIONS,
                                        value="elon_musk",
                                        id="celeb-dropdown",
                                        clearable=False
                                    ),
                             html.Div(id="flight-info-box", className="container", children=[
                                        html.Div(id="cost-div", className="box", children=f"This flight cost: ${1}"),
                                        html.Div(id="co2-div", className="box", children=f"This flight produced {1} mtCO2"),
                                        html.Div(id="fuel-div", className="box",children=f"This flight used {1} gal of fuel"),
                                        html.Div(id="time-div", className="box",children=f"This flight took {1} hour(s)"),
                                    ]),
                             
                             html.Div(id="infographic-box", className="container", children=[
                                 dcc.Interval(id="refresh_infographic", interval=5*1000, n_intervals=0),
                                 html.P(id='infographic-text', className="box", children="The infographic text will go here")
                             ]),
                             html.Div(id="small-analytics-container", children=[
                                 html.Div(id="co2-graph-container", children=[
                                     dcc.Graph(id="co2-graph",
                                        figure=co2_of_flight_vs_average({"owner": "elon", "co2": 100}, 20))
                                 ]),
                                 html.Div(id="cost-graph-container", children=[
                                     dcc.Graph(id="cost-graph",
                                        figure=cost_of_flight_vs_average({"owner": "elon", "cost": 1000, "time": 2}, 15))
                                 ])
                             ])
                         ]),
                html.Div(id="map-column",
                         children=[
                            html.Div(id='map-container-vert-pad'),
                            html.Div(id='slider-container', children=[
                                         html.P(id='slider-text', children="Move slider to see past flights"),
                                         dcc.Slider(id="previous-flight-slider",
                                                    min=min(PAST_FLIGHTS), max=max(PAST_FLIGHTS), step=1,
                                                    marks={str(year): { "label": str(year),
                                                                       "style": {"color": "#7fafdf"},
                                                                       } for year in PAST_FLIGHTS
                                                    },
                                                )]
                                     ),
                            html.Div(id="flight-map-container", children=[
                                     dcc.Graph(id="flight-map",
                                        figure=create_flight_map(TEMP_FLIGHT))
                                 ]),
                            html.Div(id="graph-flights-over-time",children=[
                                     dcc.Graph(id="flights-vs-time-graph",
                                        figure=number_of_flights_over_time())
                                 ])
                         ]),
])])


@app.callback(
    [Output("celeb-info-text-name", "children"),
     Output("celeb-info-text-gender", "children"),
     Output("celeb-info-text-age", "children"),
     Output("celeb-info-text-worth", "children"),
     Output("celeb-img", "src"),
     Output("num-flights-tracked", "children"),
     Output("previous-flight-slider", "min"),
     Output("previous-flight-slider", "max"),
    ],
    Input("celeb-dropdown", "value"),
)
def swap_celebrity(dropdown_value:str):
    """ This is a callback for the dropdown list to pipe data into all the elements """
    celeb_name = " ".join([x[0].upper() + x[1:] for x in dropdown_value.split('_')])
    name, gender, age, worth = get_celeb_info(celeb_name, owner_df, gender_df)
    celeb_img = f"assets/celeb_photos/{dropdown_value}.jpg"
    number_of_flights_tracked = get_number_of_flights(celeb_name, owner_df, aircraft_df, flight_df)
    
    minimum_number_flights = 1
    maximum_number_flights = 5

    return name, gender, age, worth, celeb_img, number_of_flights_tracked, minimum_number_flights, \
            maximum_number_flights



@app.callback(
    Output("infographic-text", "children"),
    Input("infographic-text", "children"),
    Input("refresh_infographic", "n_intervals"),
)
def swap_infographic(n_intervals:str, previous_text:str) -> str:
    """ Swaps the infographic image every 5 seconds between CO2, cost, fuel volume, and time """
    previous_text = np.random.choice(["co2", "cost", "fuel", "time"])
    
    for quantity in ["co2", "cost", "fuel", "time"]:
        if quantity in previous_text.lower():
            new_text = get_new_infographic_text(previous=quantity)
            break
    return new_text




if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080, use_reloader=True)


    