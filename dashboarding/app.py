""" This module hosts the jet radar page """
import os
import numpy as np
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dotenv import load_dotenv
from visualisation_functions import default_empty_fig,default_flight_fig, num_of_flights_over_time
from visualisation_functions import cost_flight_vs_avg, create_flight_map,co2_flight_vs_avg
from db_connections import get_data_as_dataframe, SQLconnection
from conversion_metrics import get_most_recent_flight_info
from conversion_metrics import get_celeb_info, get_total_number_of_flights, get_flight_time
from conversion_metrics import get_flight_cost, get_flight_co2
from conversion_metrics import get_new_infographic_text
from conversion_metrics import CELEB_DROPDOWN_OPTIONS

load_dotenv()

app = Dash(__name__, use_pages=False)
app.title = "JetRADAR"
server = app.server

# Get data
sql_conn = SQLconnection(config=os.environ)
owner_df = get_data_as_dataframe(sql_conn, "owner")
aircraft_df = get_data_as_dataframe(sql_conn, "aircraft")
model_df = get_data_as_dataframe(sql_conn, "model")
flight_df = get_data_as_dataframe(sql_conn, "flight")
gender_df = get_data_as_dataframe(sql_conn, "gender")
airport_df=get_data_as_dataframe(sql_conn, "airport")


MEDIAN_HR_WAGE = 11.01*100 # Median hrly wage for 100 Americans
AVG_YEARLY_CO2_IMPACT = 4 # mtCO2: GLOBAL AVG YEARLY CO2 of 4tons * 1000 people

previous_infographic = "time" # sets a default to work from
PAST_FLIGHTS = [1, 2, 3, 4, 5]
focused_name='Elon Musk'
owner_initial = owner_df[owner_df["name"] == "Elon Musk"]
most_recent_flights= get_most_recent_flight_info(owner_initial, flight_df, aircraft_df, airport_df)
recent_co2, recent_cost, recent_fuel, recent_time = 0,0,0,0


dep_time, arr_time = most_recent_flights['dep_time'][0],most_recent_flights['arr_time'][0]
recent_display, recent_time = get_flight_time(dep_time, arr_time)

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
                            html.Div(id="flights-tracked-container", className="container",
                                      children=[
                                            html.P(id="num-flights-tracked",className="box"),
                                        ]),
                        ]),
                html.Div(id="center-column",
                         children=[
                             html.H4(id="title",
                                     children="Visualisation of private jet emissions & costs"),
                             html.P(id="description",
                                    children="Climate Change is a fundamental political issue, \
                                        with 75% of adults in Britain at least somewhat worried \
                                        about the climate. It can be difficult to understand the\
                                        impact that a small set of people have compared to the \
                                        rest of us - this tool visualises their impact."),
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
                                 dcc.Interval(id="refresh_infographic",
                                              interval=5*1000, n_intervals=0),
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
                                         html.P(id='slider-text',
                                            children="Move slider for up to 5 previous flights"),
                                         dcc.Slider(id="previous-flight-slider",
                                                    min=min(PAST_FLIGHTS), max=max(PAST_FLIGHTS),
                                                    step=1, value=1,
                                                    marks={str(year):
                                                           { "label": str(year),
                                                            "style": {"color": "#7fafdf"},
                                                            } for year in PAST_FLIGHTS
                                                    },
                                                )]
                                     ),
                            html.Div(id="flight-map-container", children=[
                                     dcc.Graph(id="flight-map")
                                 ]),
                            html.Div(id="graph-flights-over-time",children=[
                                     dcc.Graph(id="flights-vs-time-graph")
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

     Output("co2-graph","figure"),
     Output("cost-graph","figure"),
     Output("flight-map","figure"),
     Output("flights-vs-time-graph","figure"),
    ],
    [Input("celeb-dropdown", "value")],
)
def swap_celebrity(dropdown_value:str):
    """ This is a callback for the dropdown list to pipe data into all the elements """
    #sets them to alter the global values
    global recent_cost, recent_co2, recent_fuel, recent_time, recent_display
    global most_recent_flights, focused_name
    celeb_name = " ".join([x[0].upper() + x[1:] for x in dropdown_value.split('_')])
    name, gender, age, worth = get_celeb_info(celeb_name, owner_df, gender_df)
    focused_name = name
    celeb_img = f"assets/celeb_photos/{dropdown_value}.jpg"
    num_tracked_flights = get_total_number_of_flights(celeb_name, owner_df, aircraft_df, flight_df)

    curr_owner = owner_df[owner_df["name"] == name]
    most_recent_flights = get_most_recent_flight_info(curr_owner,flight_df,aircraft_df,airport_df)


    # Set defaults for when we don't have flights yet
    flight_cost_string = "This flight cost - "
    flight_co2_string = "This flight used - "
    flight_fuel_string = "This flight used - "
    flight_time_string = "This flight took - "

    recent_cost, recent_co2, recent_fuel, recent_time = 0,0,0,0
    cost_fig, co2_fig = default_empty_fig(), default_empty_fig()
    flight_fig, weekday_fig = default_flight_fig(), default_empty_fig()

    if most_recent_flights['fuel_usage'] != {}:
        recent_cost = get_flight_cost(most_recent_flights['fuel_usage'][0])
        recent_co2 =  get_flight_co2(most_recent_flights['fuel_usage'][0])
        recent_fuel = round(most_recent_flights['fuel_usage'][0])

        d_time,a_time = most_recent_flights['dep_time'][0],most_recent_flights['arr_time'][0]
        recent_display, recent_time = get_flight_time(d_time, a_time)

        flight_cost_string += f"${recent_cost}"
        flight_co2_string += f"{recent_co2} mtCO2"
        flight_fuel_string +=f"{recent_fuel} gal of fuel"
        flight_time_string += f"{recent_display}"

        f_data_cost = {"owner":name,"cost":recent_cost, "time":recent_time}
        f_data_co2 = {"owner": name, "co2": recent_co2}
        cost_fig = cost_flight_vs_avg(f_data_cost, MEDIAN_HR_WAGE)
        co2_fig = co2_flight_vs_avg(f_data_co2, AVG_YEARLY_CO2_IMPACT)

        lat_i = most_recent_flights["lat_dep_airport"][0]
        lat_j = most_recent_flights["lat_arr_airport"][0]
        lon_i = most_recent_flights["lon_dep_airport"][0]
        lon_j = most_recent_flights["lon_arr_airport"][0]

        flight_fig = create_flight_map({'Location': ['Start', 'End'],
                                        'lat': [lat_i, lat_j],
                                        'long': [lon_i, lon_j]})
        weekday_fig = num_of_flights_over_time(most_recent_flights)

    return "Name:"+name, "Gender: "+gender, "Age: "+age,"Worth: "+ worth, \
          celeb_img, num_tracked_flights, flight_cost_string, flight_co2_string, \
            flight_fuel_string, flight_time_string, co2_fig, cost_fig, flight_fig, weekday_fig



@app.callback(
    Output("infographic-text", "children"),
    Input("refresh_infographic", "n_intervals"),
)
def swap_infographic(n_intervals:int) -> str:
    """ Swaps the infographic image every 5 seconds between CO2, cost, fuel volume, and time """
    comparison_choice = np.random.choice(["co2", "cost", "fuel", "time"])

    if comparison_choice == "co2":
        return get_new_infographic_text('co2', recent_co2)
    if comparison_choice == "cost":
        return get_new_infographic_text('cost', recent_cost)
    if comparison_choice == "fuel":
        return get_new_infographic_text('fuel', recent_fuel)
    if comparison_choice == "time":
        return get_new_infographic_text('time', recent_time)

    raise ValueError("comparison_choice should only ever be one of ['time', 'fuel', 'co2', 'cost']")

@app.callback(
    [Output("cost-div", "children", allow_duplicate=True),
     Output("co2-div", "children", allow_duplicate=True),
     Output("fuel-div", "children", allow_duplicate=True),
     Output("time-div", "children", allow_duplicate=True),

     Output("co2-graph","figure", allow_duplicate=True),
     Output("cost-graph","figure", allow_duplicate=True),
     Output("flight-map","figure", allow_duplicate=True),
     Output("flights-vs-time-graph","figure", allow_duplicate=True),
    ],
    Input("previous-flight-slider", "value"), prevent_initial_call=True
)
def change_flights(flight_index: int) -> str:
    """ Change flights via slider NOTE:repeated code, clean this up """
    max_index_of_flights_available = len(list(most_recent_flights["fuel_usage"].keys()))-1
    flight_index = min(flight_index-1, max_index_of_flights_available)

    if flight_index <= max_index_of_flights_available:
        # Set defaults for when we don't have flights yet
        return recalculate_flight_data(flight_index)

    return "No Data", "No Data", "No Data", "No Data", \
        default_empty_fig(), default_empty_fig(), default_flight_fig(), default_empty_fig()


def recalculate_flight_data(flight_idx:int):
    """ Calculates the displayed flight data """

    flight_cost_string = "This flight cost - "
    flight_co2_string = "This flight used - "
    flight_fuel_string = "This flight used - "
    flight_time_string = "This flight took - "
    recent_cost, recent_co2, recent_fuel, recent_time = 0,0,0,0
    cost_fig, co2_fig = default_empty_fig(), default_empty_fig()
    flight_fig, weekday_fig = default_flight_fig(), default_empty_fig()

    if most_recent_flights['fuel_usage'] != {}:
        recent_cost = get_flight_cost(most_recent_flights['fuel_usage'][flight_idx])
        recent_co2 =  get_flight_co2(most_recent_flights['fuel_usage'][flight_idx])
        recent_fuel = round(most_recent_flights['fuel_usage'][flight_idx])

        d_time = most_recent_flights['dep_time'][flight_idx]
        a_time = most_recent_flights['arr_time'][flight_idx]
        recent_display, recent_time = get_flight_time(d_time, a_time)

        flight_cost_string += f"${recent_cost}"
        flight_co2_string += f"{recent_co2} mtCO2"
        flight_fuel_string +=f"{recent_fuel} gal of fuel"
        flight_time_string += f"{recent_display}"

        f_data_cost = {"owner":focused_name,"cost":recent_cost, "time":recent_time}
        f_data_co2 = {"owner": focused_name, "co2": recent_co2}
        cost_fig = cost_flight_vs_avg(f_data_cost, MEDIAN_HR_WAGE)
        co2_fig = co2_flight_vs_avg(f_data_co2, AVG_YEARLY_CO2_IMPACT)

        lat_i = most_recent_flights["lat_dep_airport"][flight_idx]
        lat_j = most_recent_flights["lat_arr_airport"][flight_idx]
        lon_i = most_recent_flights["lon_dep_airport"][flight_idx]
        lon_j = most_recent_flights["lon_arr_airport"][flight_idx]

        flight_fig = create_flight_map({'Location': ['Start', 'End'],
                                        'lat': [lat_i, lat_j], 'long': [lon_i, lon_j]})
        weekday_fig = num_of_flights_over_time(most_recent_flights)

    return flight_cost_string, flight_co2_string, flight_fuel_string, flight_time_string, co2_fig, \
        cost_fig, flight_fig, weekday_fig


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8080)
