import pandas as pd
import os
from dash import Dash, html, dcc, page_container, page_registry
from dotenv import load_dotenv
from dash.dependencies import Input, Output, State
from visualisation_functions import default_empty_fig, co2_of_flight_vs_average, cost_of_flight_vs_average, number_of_flights_over_time, create_flight_map
from db_connections import get_data_as_dataframe, SQLconnection
from conversion_metrics import get_most_recent_flight_info
from conversion_metrics import get_celeb_info, get_total_number_of_flights
from conversion_metrics import get_flight_cost, get_flight_co2, get_flight_time
from conversion_metrics import get_new_infographic_text
import numpy as np


from conversion_metrics import UNICODE, CELEB_DROPDOWN_OPTIONS

load_dotenv()

app = Dash(__name__, use_pages=False)
app.title = "MuskJet 2.0"
server = app.server

# Get data
sql_conn = SQLconnection(config=os.environ)
owner_df = get_data_as_dataframe(sql_conn, "owner")
aircraft_df = get_data_as_dataframe(sql_conn, "aircraft")
model_df = get_data_as_dataframe(sql_conn, "model")
flight_df = get_data_as_dataframe(sql_conn, "flight")
gender_df = get_data_as_dataframe(sql_conn, "gender")
airport_df=get_data_as_dataframe(sql_conn, "airport")


MEDIAN_HR_WAGE = 11.01*100 # Median hrly wage for 100 Americans https://www.statista.com/statistics/216259/monthly-real-average-hourly-earnings-for-all-employees-in-the-us/
AVG_YEARLY_CO2_IMPACT = 4 # mtCO2: GLOBAL AVG YEARLY CO2 of 4tons * 1000 people

TEMP_FLIGHT = {'Location': ['Start', 'End'], 'lat': [30, 40], 'long': [-90, -80]}
DEFAULT_NAME="Elon Musk"
DEFAULT_GENDER="Male"
DEFAULT_AGE = 51
DEFAULT_WORTH="180000 M"

PREVIOUS_INFOGRAPHIC = "time" # sets a default to work from
PAST_FLIGHTS = [1, 2, 3, 4, 5]
MOST_RECENT_FLIGHTS= get_most_recent_flight_info(owner_df[owner_df["name"] == DEFAULT_NAME], flight_df, aircraft_df, airport_df)

RECENT_FUEL = round(MOST_RECENT_FLIGHTS['fuel_usage'][0])
RECENT_CO2 = get_flight_co2(RECENT_FUEL)
RECENT_COST = get_flight_cost(RECENT_FUEL)
RECENT_DISPLAY, RECENT_TIME = get_flight_time(MOST_RECENT_FLIGHTS['dep_time'][0],MOST_RECENT_FLIGHTS['arr_time'][0])

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
                                    html.Li(id='celeb-info-text-name'),
                                    html.Li(id='celeb-info-text-gender'),
                                    html.Li(id='celeb-info-text-age'),
                                    html.Li(id='celeb-info-text-worth')]),
                                 ]),
                            html.Div(id="flights-tracked-container", className="container", children=[
                                html.P(id="num-flights-tracked",className="box"),
                            ]),
                        ]),
                html.Div(id="center-column",
                         children=[
                             html.H4(id="title", children="Visualisation of private jet emissions & costs"),
                             html.P(id="description", children="Climate Change is a fundamental political issue, with \
                                                                75% of adults in Britain at least somewhat worried about the climate. \
                                                                It can be difficult to understand the impact that a small set of people \
                                                                have compared to the rest of us - this tool aims to fix that."),
                             dcc.Dropdown(
                                        options=CELEB_DROPDOWN_OPTIONS,
                                        value="elon_musk",
                                        id="celeb-dropdown",
                                        clearable=False
                                    ),
                             html.Div(id="flight-info-box", className="container", children=[
                                        html.Div(id="cost-div", className="box"),
                                        html.Div(id="co2-div", className="box"),
                                        html.Div(id="fuel-div", className="box"),
                                        html.Div(id="time-div", className="box"),
                                    ]),
                             
                             html.Div(id="infographic-box", className="container", children=[
                                 html.Div(id="hidden-hold-"),
                                 dcc.Interval(id="refresh_infographic", interval=5*1000, n_intervals=0),
                                 html.P(id='infographic-text', className="box")
                             ]),
                             html.Div(id="small-analytics-container", children=[
                                 html.Div(id="co2-graph-container", children=[
                                     dcc.Graph(id="co2-graph")
                                 ]),
                                 html.Div(id="cost-graph-container", children=[
                                     dcc.Graph(id="cost-graph")
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

     Output("cost-div", "children"),
     Output("co2-div", "children"),
     Output("fuel-div", "children"),
     Output("time-div", "children"),

     Output("co2-graph", "figure"),
     Output("cost-graph", "figure"),
    ],
    Input("celeb-dropdown", "value"),
)
def swap_celebrity(dropdown_value:str):
    """ This is a callback for the dropdown list to pipe data into all the elements """
    celeb_name = " ".join([x[0].upper() + x[1:] for x in dropdown_value.split('_')])
    name, gender, age, worth = get_celeb_info(celeb_name, owner_df, gender_df)
    celeb_img = f"assets/celeb_photos/{dropdown_value}.jpg"
    number_of_flights_tracked = get_total_number_of_flights(celeb_name, owner_df, aircraft_df, flight_df)
    
    MOST_RECENT_FLIGHTS = get_most_recent_flight_info(owner_df[owner_df["name"] == name], flight_df, aircraft_df, airport_df)
    
    # Set defaults for when we don't have flights yet
    flight_cost_string = "This flight cost - "
    flight_co2_string = "This flight used - "
    flight_fuel_string = "This flight used - "
    flight_time_string = "This flight took - "
    cost_fig, co2_fig = default_empty_fig(), default_empty_fig()

    if MOST_RECENT_FLIGHTS['fuel_usage'] != {}:
        #sets them to alter the global values
        global RECENT_COST, RECENT_CO2, RECENT_FUEL, RECENT_TIME, RECENT_DISPLAY 
        RECENT_COST = get_flight_cost(MOST_RECENT_FLIGHTS['fuel_usage'][0])
        RECENT_CO2 =  get_flight_co2(MOST_RECENT_FLIGHTS['fuel_usage'][0])
        RECENT_FUEL = round(MOST_RECENT_FLIGHTS['fuel_usage'][0])
        RECENT_DISPLAY, RECENT_TIME = get_flight_time(MOST_RECENT_FLIGHTS['dep_time'][0],MOST_RECENT_FLIGHTS['arr_time'][0])

        flight_cost_string += f"${RECENT_COST}"
        flight_co2_string += f"{RECENT_CO2} mtCO2"
        flight_fuel_string +=f"{RECENT_FUEL} gal of fuel"
        flight_time_string += f"{RECENT_DISPLAY}"
        cost_fig = cost_of_flight_vs_average({"owner": name, "cost": RECENT_COST, "time":RECENT_TIME}, MEDIAN_HR_WAGE)
        co2_fig = co2_of_flight_vs_average({"owner": name, "co2": RECENT_CO2}, AVG_YEARLY_CO2_IMPACT)


    return "Name:"+name, "Gender: "+gender, "Age: "+age,"Worth: "+ worth, \
          celeb_img, number_of_flights_tracked, flight_cost_string, flight_co2_string, \
            flight_fuel_string, flight_time_string, co2_fig, cost_fig



@app.callback(
    Output("infographic-text", "children"),
    Input("refresh_infographic", "n_intervals"),
)
def swap_infographic(n_intervals) -> str:
    """ Swaps the infographic image every 5 seconds between CO2, cost, fuel volume, and time """
    comparison_choice = np.random.choice(["co2", "cost", "fuel", "time"])

    if comparison_choice == "co2":
        return get_new_infographic_text('co2', RECENT_CO2)
    elif comparison_choice == "cost":
        return get_new_infographic_text('cost', RECENT_COST)
    elif comparison_choice == "fuel":
        return get_new_infographic_text('fuel', RECENT_FUEL)
    elif comparison_choice == "time":
        return get_new_infographic_text('time', RECENT_TIME)
    else:
        raise ValueError("comparison_choice should only ever be one of ['time', 'fuel', 'co2', 'cost']")


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080, use_reloader=True)


    