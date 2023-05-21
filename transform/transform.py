import json
import os
from math import sin, cos, acos, pi
from datetime import datetime
from typing import Generator
import country_converter as coco
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv
import pandas as pd
from s3fs import S3FileSystem


AIRPORTS_JSON = "airports.json"
AIRCRAFTS_JSON= "aircraft_fuel_consumption_rates.json"
JET_OWNERS_JSON = "jet_owners.json"
BUCKET_NAME = "jet-bucket"
STAGING_SCHEMA = "staging"
PRODUCTION_SCHEMA = "production"


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


def load_json_file_from_s3(file_name: str, bucket_name: str = BUCKET_NAME) -> object:
    """Reads a json file from an s3 bucket and returns the object. Requires the names of the bucket
    and file as strings."""

    s3 = S3FileSystem(key=config["ACCESS_KEY_ID"],
                      secret=config["SECRET_ACCESS_KEY"])
    
    return json.load(s3.open(path=f"{bucket_name}/{file_name}"))


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
    """Parses events from staging db and extracts flight number, tail number, departure time/location
    and arrival time/location. Yields these values as a tuple. Expects staging DB connection object."""

    df = pd.read_sql("SELECT * FROM tracked_event;", conn)
    curs = conn.cursor(cursor_factory=RealDictCursor)

    jets = df["aircraft_reg"].unique()
    for jet in jets:
        flight = df[df["aircraft_reg"] == jet].sort_values("time_input").reset_index().to_dict('records')

        emergency = flight[-1]["emergency"]
    
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

                seconds_since_last_event = (pd.Timestamp.now() - arr_time).total_seconds()
                if seconds_since_last_event < 30*60:
                    break
                
                yield jet, flight_no, dep_time, dep_location, arr_time, arr_location, emergency
                curs.execute("DELETE FROM tracked_event WHERE aircraft_reg = %s AND time_input <= %s",
                             (jet, arr_time))
            else:
                arr_time = previous_event["time_input"]
                arr_location = (previous_event["lat"], previous_event["lon"])

                yield jet, flight_no, dep_time, dep_location, arr_time, arr_location, emergency
                curs.execute("DELETE FROM tracked_event WHERE aircraft_reg = %s AND time_input <= %s",
                             (jet, arr_time))

                dep_time = current_event["time_input"]
                dep_location = (current_event["lat"], current_event["lon"])


def insert_airport_info(conn: connection, airport_info: dict[dict]) -> None:
    """Inserts airport data into production db and populates country/ continent tables.
    Expects the production db connection object and the airport data."""
    
    curs = conn.cursor(cursor_factory=RealDictCursor)
    curs.execute("SELECT * FROM airport LIMIT 1")
    if curs.fetchall():
        return

    cc = coco.CountryConverter()

    continent_codes = {"Asia": "AS", "Europe": "EU", "Africa": "AF", "Oceania": "OC", "America": "AM"}

    for airport in airport_info:
        name = airport_info[airport]["name"]
        iata = airport_info[airport]["iata"]
        lat = airport_info[airport]["lat"]
        lon = airport_info[airport]["lon"]
        try:
            country = airport_info[airport]["iso"]
            country_name = cc.convert(names=country, to="name_short")
            continent_name = cc.convert(names=country, to="continent")
            continent = continent_codes[continent_name]
        except Exception:
            continue

        curs.execute("SELECT country_id FROM country WHERE code = %s", (country,))
        country_id = curs.fetchall()

        if not country_id:
            curs.execute("SELECT continent_id FROM continent WHERE code = %s", (continent,))
            continent_id = curs.fetchall()
            if not continent_id:
                curs.execute("INSERT INTO continent (code, name) VALUES (%s, %s) RETURNING continent_id",
                             (continent, continent_name))
                continent_id = dict(curs.fetchall()[0])["continent_id"]
            else:
                continent_id = dict(continent_id[0])["continent_id"]
            curs.execute("INSERT INTO country (code, name, continent_id) VALUES (%s, %s, %s) RETURNING country_id",
                         (country, country_name, continent_id))
            country_id = dict(curs.fetchall()[0])["country_id"]
        else:
            country_id = dict(country_id[0])["country_id"]

        curs.execute("INSERT INTO airport (name, iata, lat, lon, country_id) VALUES (%s, %s, %s, %s, %s)",
                     (name, iata, lat, lon, country_id))

    curs.close()


def insert_jet_owner_info(conn: connection, aircraft_info: dict[dict], owner_info: list[dict]) -> None:
    """Inserts jet owner data """

    curs = conn.cursor(cursor_factory=RealDictCursor)

    for owner in owner_info:
        
        tail_number = owner["tail_number"]

        curs.execute("SELECT * FROM aircraft WHERE tail_number = %s", (tail_number,))
        if curs.fetchall():
            continue

        name = owner["name"]
        gender = owner["gender"]
        est_net_worth = owner["est_net_worth"]
        birthdate = owner["birthdate"]
        if birthdate:
            birthdate = datetime.strptime(birthdate, "%d/%m/%Y")
        job_roles = owner["job_role"]
        aircraft_model = owner["aircraft_model"]

        if gender:
            curs.execute("SELECT gender_id FROM gender WHERE name = %s", (gender,))
            gender_id = curs.fetchall()
            if not gender_id:
                curs.execute("INSERT INTO gender (name) VALUES (%s) RETURNING gender_id", (gender,))
                gender_id = dict(curs.fetchall()[0])["gender_id"]
            else:
                gender_id = dict(gender_id[0])["gender_id"]
        else:
            gender_id = None

        curs.execute("SELECT owner_id FROM owner WHERE name = %s", (name,))
        owner_id = curs.fetchall()
        if not owner_id:
            curs.execute("INSERT INTO owner (name, gender_id, est_net_worth, birthdate) VALUES (%s, %s, %s, %s) RETURNING owner_id",
                         (name, gender_id, est_net_worth, birthdate))
            owner_id = dict(curs.fetchall()[0])["owner_id"]
        else:
            owner_id = dict(owner_id[0])["owner_id"]

        if aircraft_model:
            aircraft_model_name = aircraft_info[aircraft_model]["name"]
            fuel_efficiency = aircraft_info[aircraft_model]["galph"]

            curs.execute("SELECT model_id FROM model WHERE code = %s", (aircraft_model,))
            model_id = curs.fetchall()
            if not model_id:
                curs.execute("INSERT INTO model (code, name, fuel_efficiency) VALUES (%s, %s, %s) RETURNING model_id",
                            (aircraft_model, aircraft_model_name, fuel_efficiency))
                model_id = dict(curs.fetchall()[0])["model_id"]
            else:
                model_id = dict(model_id[0])["model_id"]
        else:
            model_id = None

        curs.execute("INSERT INTO aircraft (tail_number, model_id, owner_id) VALUES (%s, %s, %s)",
                     (tail_number, model_id, owner_id))
        
        for job_role in job_roles:
            curs.execute("SELECT job_role_id FROM job_role WHERE name = %s", (job_role,))
            job_role_id = curs.fetchall()
            if not job_role_id:
                curs.execute("INSERT INTO job_role (name) VALUES (%s) RETURNING job_role_id", (job_role,))
                job_role_id = dict(curs.fetchall()[0])["job_role_id"]
            else:
                job_role_id = dict(job_role_id[0])["job_role_id"]

            curs.execute("INSERT INTO owner_role_link (owner_id, job_role_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                         (owner_id, job_role_id))

    curs.close()


def insert_todays_flights(prod_conn: connection, staging_conn: connection, airport_info: dict[dict], aircraft_info: dict[dict]) -> None:
    """Inserts todays flights into the database. Expects a production connection object."""
    
    curs = prod_conn.cursor(cursor_factory=RealDictCursor)

    for flight in extract_todays_flights(staging_conn):
        tail_number, flight_no, dep_time, dep_location, arr_time, arr_location, emergency = flight

        print(tail_number)

        dep_airport = find_nearest_airport(*dep_location, airport_info)
        arr_airport = find_nearest_airport(*arr_location, airport_info)
        if dep_airport == arr_airport: continue

        curs.execute("SELECT airport_id FROM airport WHERE iata = %s", (dep_airport,))
        dep_airport_id = dict(curs.fetchall()[0])["airport_id"]
        curs.execute("SELECT airport_id FROM airport WHERE iata = %s", (arr_airport,))
        arr_airport_id = dict(curs.fetchall()[0])["airport_id"]

        curs.execute("""SELECT code FROM model JOIN aircraft ON model.model_id = aircraft.model_id
                     WHERE aircraft.tail_number = %s""", (tail_number,))
        aircraft_model = curs.fetchall()
        if aircraft_model:
            aircraft_model = dict(aircraft_model[0])["code"]
            fuel_usage = calculate_fuel_consumption(dep_time, arr_time, aircraft_model, aircraft_info)
        else:
            fuel_usage = None

        curs.execute("SELECT emergency_id FROM emergency WHERE type = %s", (emergency,))
        emergency_id = curs.fetchall()
        if not emergency_id:
            curs.execute("INSERT INTO emergency (type) VALUES (%s) RETURNING emergency_id", (emergency,))
            emergency_id = dict(curs.fetchall()[0])["emergency_id"]
        else:
            emergency_id = dict(emergency_id[0])["emergency_id"]

        print(emergency_id)

        curs.execute("""INSERT INTO flight (flight_number, dep_airport_id, arr_airport_id, dep_time, arr_time, tail_number,
                     emergency_id, fuel_usage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                     (flight_no, dep_airport_id, arr_airport_id, dep_time, arr_time, tail_number, emergency_id, fuel_usage))
    
    curs.close()




if __name__ == "__main__":

    airport_info = load_json_file_from_s3(AIRPORTS_JSON)
    aircraft_info = load_json_file_from_s3(AIRCRAFTS_JSON)
    jet_owners_info = load_json_file_from_s3(JET_OWNERS_JSON)

    staging_conn = get_db_connection(STAGING_SCHEMA)
    production_conn = get_db_connection(PRODUCTION_SCHEMA)

    insert_airport_info(production_conn, airport_info)

    insert_jet_owner_info(production_conn, aircraft_info, jet_owners_info)

    insert_todays_flights(production_conn)

    production_conn.commit()
    staging_conn.commit()

    production_conn.close()
    staging_conn.close()
