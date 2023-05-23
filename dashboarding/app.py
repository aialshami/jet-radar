import pandas as pd
import os
from dash import Dash, html, dcc, page_container, page_registry
from dotenv import load_dotenv
from dash.dependencies import Input, Output, State
from visualisation_functions import co2_of_flight_vs_average, cost_of_flight_vs_average, number_of_flights_over_time, create_flight_map
from db_connections import get_data_as_dataframe, SQLconnection
from conversion_metrics import get_age_from_birthdate, get_gender_from_id, get_net_worth_as_million_dollars, get_most_recent_flight_info


load_dotenv()
TEMP_FLIGHT = {'Location': ['Start', 'End'], 'lat': [30, 40], 'long': [-90, -80]}


# Unicode chars
UNICODE = {"cow": "\U0001F42E", "car": "\U0001F697", "plane": "\U0001F6E9", 
           "tree": "\U0001F333", "sun": "\U0001F324", "football": "\U000026BD",
           "watch":"\U000023F1", "music":"\U0001F3B5", "phone": "\U0001F4F1",
           "money":"\U0001F4B0", "film":"\U0001F3A5", "sweets":"\U0001F36C", 
           "shopping": "\U0001F6D2", "tea":"\U00002615", "beer": "\U0001F37A"}

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

# Derive display values for celeb
owner = owner_df[owner_df["name"] == "Floyd Mayweather"]
name, age = 'Floyd Mayweather', get_age_from_birthdate(owner["birthdate"].values[0])
print(name, age)
gender = get_gender_from_id(owner["gender_id"].values[0], gender_df)
worth = get_net_worth_as_million_dollars(owner['est_net_worth'].values[0])
print(gender, worth)

# Derive display values for the flight
fuel_used, co2_used = "no full flight found", "no full flight found"
flight_cost, flight_time = "no full flight found", "no full flight found"

most_recent_flight = get_most_recent_flight_info(owner, flight_df, aircraft_df, )
if most_recent_flight is not None:
    fuel_used = most_recent_flight['fuel_used']





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
                                    html.Li(id='celeb-info-text-name', children=f"Name: {name}"),
                                    html.Li(id='celeb-info-text-gender', children=f"Gender: {gender}"),
                                    html.Li(id='celeb-info-text-age', children=f"Age: {age}"),
                                    html.Li(id='celeb-info-text-worth', children=f"Worth: {worth}")]),
                                 ]),
                            html.Div(id="flights-tracked-container", className="container", children=[
                                html.P(id="num-flights-tracked",className="box", children="# of flights tracked is: 5"),
                            ]),
                             
                        ]),
                html.Div(id="center-column",
                         children=[
                             html.H4(id="title", children="Visualisation of private jet emissions & costs"),
                             html.P(id="description", children="It's hard to understand how bad these planes are - this helps."),
                             
                             html.Div(id="flight-info-box", className="container", children=[
                                        html.Div(id="cost-div", className="box", children=f"This flight cost: ${1}"),
                                        html.Div(id="co2-div", className="box", children=f"This flight produced {1} mtCO2"),
                                        html.Div(id="fuel-div", className="box",children=f"This flight used {1} gal of fuel"),
                                        html.Div(id="time-div", className="box",children=f"This flight took {1} hour(s)"),
                                    ]),
                             
                             html.Div(id="infographic-box", className="container", children=[
                                 html.P(id='infographic-text', className="box", children="This box will contain infographics on co2 etc")
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


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080, use_reloader=True)


    