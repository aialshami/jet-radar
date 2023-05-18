import json
import os
from math import sin, cos, acos, pi
from datetime import datetime
from typing import Generator
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection
from dotenv import load_dotenv
import pandas as pd


AIRPORTS_JSON_FILE_PATH = "./airports.json"
AIRCRAFT_INFO_JSON_FILE_PATH = "./aircraft_fuel_consumption_rates.json"


load_dotenv()
config = os.environ


def get_db_connection(schema: str) -> connection:
    """Establishes connection to database. Returns psycopg2 connection object.
    Expects schema name as string."""

    return psycopg2.connect(user = config["DATABASE_USERNAME"],
                            password = config["DATABASE_PASSWORD"],
                            host = config["DATABASE_IP"],
                            port = config["DATABASE_PORT"],
                            database = config["DATABASE_NAME"],
                            options = f"-c search_path={schema}")


def load_airport_info(data_file_path: str = AIRPORTS_JSON_FILE_PATH) -> dict:
    """Returns a dictionary with airport codes as keys and the location of the 
    airport in a latitude, longitude tuple as values. Expects a file path as input."""

    with open(data_file_path, encoding="utf-8") as f:
        airport_data = json.load(f)

    return {airport["iata"]: airport for airport in airport_data 
            if "lat" in airport and "lon" in airport}


def load_aircraft_info(data_file_path: str = AIRCRAFT_INFO_JSON_FILE_PATH) -> dict[dict]:
    """Returns data on aircraft models including the name, fuel consumption and category as 
    a dictionary of dictionaries. Expects a file path as input."""

    with open(data_file_path, encoding="utf-8") as f:
        return json.load(f)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates distance in km between two locations. The latitudes and longitudes are 
    converted to radians and the distance is calculated using the Haversine formula. 
    r is the radius of the earth. Expects floats and returns a float."""

    r = 6371
    lat1_rad = lat1 * pi/180
    lat2_rad = lat2 * pi/180
    lon1_rad = lon1 * pi/180
    lon2_rad = lon2 * pi/180

    return acos(sin(lat1_rad)*sin(lat2_rad) + cos(lat1_rad)*cos(lat2_rad)*cos(lon2_rad-lon1_rad)) * r


def find_nearest_airport(lat: float, lon: float, airport_locations: dict) -> str:
    """Finds closest airport to input latitude and longitude and returns the airport IATA code and
    location. Expects latitude and longitude as floats and a dictionary of airport locations."""

    return sorted(airport_locations.items(),
                  key=lambda x: haversine_distance(float(x[1]["lat"]), float(x[1]["lon"]), lat, lon))[0][0]


def calculate_fuel_consumption(dep_time: datetime, arr_time: datetime, aircraft_model: str,
                               aircraft_info: dict[dict]) -> float:
    """Calculates fuel consumption by multiplying the flight duration in hours by the estimated 
    fuel consumption of the aircraft. Returns this as a float in gallons (galph = gallons per hour). 
    Expects departure/arrival times as datetimes, the aircraft model code and aircraft info.
    """

    flight_duration_hours = (arr_time - dep_time).hours
    fuel_consumption_rate = aircraft_info[aircraft_model]["galph"]

    return flight_duration_hours * fuel_consumption_rate


def extract_todays_flights(conn: connection) -> Generator[tuple, None, None]:
    """"""

    df = pd.read_sql("SELECT * FROM tracked_event;", conn)

    jets = df["aircraft_reg"].unique()
    for jet in jets:
        flight = df[df["aircraft_reg"] == jet].sort_values("time_input").reset_index().to_dict('records')
    
        flight_no = flight[0]["flight_no"]
        if flight_no:
            flight_no = flight_no.strip()

        num_of_events = len(flight)
        if num_of_events == 1:
            continue

        first_event = flight[0]
        dep_time = first_event["time_input"]
        dep_location = (first_event["lat"], first_event["lon"])

        for i in range(1, num_of_events):
            current_event = flight[i]
            previous_event = flight[i-1]
            event_gap = (current_event["time_input"] - previous_event["time_input"]).total_seconds()

            if event_gap < 60*60 and i != num_of_events-1:
                continue
            elif i == num_of_events-1:
                arr_time = current_event["time_input"]
                arr_location = (current_event["lat"], current_event["lon"])

                # if arr_time is recent, jet may not have landed yet
                seconds_since_last_event = (pd.Timestamp.now() - arr_time).total_seconds()
                if seconds_since_last_event < 30*60:
                    break
                
                yield jet, flight_no, dep_time, dep_location, arr_time, arr_location
                # REMOVE RECORDS FROM STAGING DB
            else:
                arr_time = previous_event["time_input"]
                arr_location = (previous_event["lat"], previous_event["lon"])

                yield jet, flight_no, dep_time, dep_location, arr_time, arr_location
                # REMOVE RECORDS FROM STAGING DB

                dep_time = current_event["time_input"]
                dep_location = (current_event["lat"], current_event["lon"])




if __name__ == "__main__":

    airport_info = load_airport_info()
    aircraft_info = load_aircraft_info()

    staging_conn = get_db_connection("staging")
    production_conn = get_db_connection("production")

    for flight in extract_todays_flights(staging_conn):
        jet, flight_no, dep_time, dep_location, arr_time, arr_location = flight
        
        dep_airport = find_nearest_airport(*dep_location, airport_info)
        arr_airport = find_nearest_airport(*arr_location, airport_info)
        if dep_airport == arr_airport: continue

        