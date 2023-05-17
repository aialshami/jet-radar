import json
import os
from math import sin, cos, acos, pi
from datetime import datetime
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection
from dotenv import load_dotenv


AIRPORTS_JSON_FILE_PATH = "./airports.json"
AIRCRAFT_INFO_JSON_FILE_PATH = "./aircraft_fuel_consumption_rates.json"


load_dotenv()
config = os.environ


def get_db_connection() -> connection:
    """Establishes connection to database. Returns psycopg2 connection object."""

    return psycopg2.connect(user = config["DATABASE_USERNAME"],
                            password = config["DATABASE_PASSWORD"],
                            host = config["DATABASE_IP"],
                            port = config["DATABASE_PORT"],
                            database = config["DATABASE_NAME"])


def load_airport_locations(data_file_path: str = AIRPORTS_JSON_FILE_PATH) -> dict:
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
                  key=lambda x: haversine_distance(float(x[1]["lat"]), float(x[1]["lon"]), lat, lon))[0]


def calculate_fuel_consumption(dep_time: datetime, arr_time: datetime, aircraft_model: str,
                               aircraft_info: dict[dict]) -> float:
    """Calculates fuel consumption by multiplying the flight duration in hours by the estimated 
    fuel consumption of the aircraft. Returns this as a float in gallons (galph = gallons per hour). 
    Expects departure/arrival times as datetimes, the aircraft model code and aircraft info.
    """

    flight_duration_hours = (arr_time - dep_time).hours
    fuel_consumption_rate = aircraft_info[aircraft_model]["galph"]

    return flight_duration_hours * fuel_consumption_rate




if __name__ == "__main__":

    airport_locations = load_airport_locations()
    print(find_nearest_airport(52, 13.7, airport_locations))