"""This module reads tracked events from the staging database, and inserts the parsed flight information
into the production database using airports data, aircraft data and tracked owners data stored in s3."""
import json
import os
from datetime import datetime
import country_converter as coco
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor
from dotenv import load_dotenv
import pandas as pd
from s3fs import S3FileSystem

from utilities import find_nearest_airport, calculate_fuel_consumption, clean_airport_data


load_dotenv()
config = os.environ


AIRPORTS_JSON = "airports.json"
AIRCRAFTS_JSON= "aircraft_fuel_consumption_rates.json"
JET_OWNERS_JSON = "celeb_planes.json"
STAGING_SCHEMA = "staging"
PRODUCTION_SCHEMA = "production"
S3_BUCKET_NAME = "jet-bucket"


def get_db_connection(schema: str) -> connection:
    """Establishes connection to database. Returns psycopg2 connection object.
    Expects schema name as string."""

    return psycopg2.connect(user = config["DB_USER"],
                            password = config["DB_PASSWORD"],
                            host = config["DB_HOST"][:-5],
                            port = config["DB_PORT"],
                            database = config["DB_NAME"],
                            options = f"-c search_path={schema}")


def load_json_file_from_s3(file_name: str, bucket_name: str) -> list | dict:
    """Reads a json file from an s3 bucket and returns the object. Requires the names of the bucket
    and file as strings."""

    s3_session = S3FileSystem(key=config["ACCESS_KEY"],
                      secret=config["SECRET_KEY"])

    return json.load(s3_session.open(path=f"{bucket_name}/{file_name}"))


def extract_todays_flights(conn: connection) -> list[tuple]:
    """Parses events from staging db and extracts flight number, tail number, departure time/location
    and arrival time/location. Yields these values as a tuple. Expects staging DB connection object."""

    tracked_event_df = pd.read_sql("SELECT * FROM tracked_event;", conn)
    curs = conn.cursor(cursor_factory=RealDictCursor)

    parsed_flights = []

    jets = tracked_event_df["aircraft_reg"].unique()
    for jet in jets:
        flights = tracked_event_df[tracked_event_df["aircraft_reg"] == jet].reset_index()

        flight_numbers = flights["flight_no"].unique()
        for flight_no in flight_numbers:
            flight = flights[flights["flight_no"] == flight_no].sort_values("time_input").reset_index().to_dict("records")

            if not flight:
                continue

            dep_time = flight[0]["time_input"]
            dep_location = (flight[0]["lat"], flight[0]["lon"])

            arr_time = flight[-1]["time_input"]

            # if last event was within half an hour, the jet may still be in the air.
            if (pd.Timestamp.now() - arr_time).total_seconds() < 30*60:
                continue

            arr_location = (flight[-1]["lat"], flight[-1]["lon"])

            emergency = flight[-1]["emergency"]

            parsed_flights.append((jet, flight_no, dep_time, dep_location, arr_time, arr_location, emergency))
            curs.execute("DELETE FROM tracked_event WHERE aircraft_reg = %s AND flight_no = %s",
                        (jet, flight_no))

    curs.close()
    return parsed_flights


def insert_airport_info(conn: connection, airport_info: dict[dict]) -> None:
    """Inserts airport data into production db and populates country/ continent tables.
    Expects the production db connection object and the airport data."""

    curs = conn.cursor(cursor_factory=RealDictCursor)
    curs.execute("SELECT * FROM airport LIMIT 1")
    if curs.fetchall():
        return

    country_converter = coco.CountryConverter()


    continent_codes = {"Asia": "AS", "Europe": "EU", "Africa": "AF", "Oceania": "OC", "America": "AM"}

    for airport in airport_info:
        name = airport_info[airport]["name"]
        iata = airport_info[airport]["iata"]
        lat = airport_info[airport]["lat"]
        lon = airport_info[airport]["lon"]

        country = airport_info[airport]["iso"]
        country_name = country_converter.convert(names=country, to="name_short")
        continent_name = country_converter.convert(names=country, to="continent")

        if country_name == "not found" or continent_name == "not found":
            continue
        continent = continent_codes[continent_name]

        curs.execute("SELECT country_id FROM country WHERE code = %s", (country,))
        country_id = curs.fetchall()

        if not country_id:
            curs.execute("SELECT continent_id FROM continent WHERE code = %s", (continent,))
            continent_id = curs.fetchall()
            if not continent_id:
                curs.execute("INSERT INTO continent (code, name) VALUES (%s, %s) RETURNING continent_id",
                             (continent, continent_name))
                continent_id = curs.fetchall()[0]["continent_id"]
            else:
                continent_id = continent_id[0]["continent_id"]
            curs.execute("INSERT INTO country (code, name, continent_id) VALUES (%s, %s, %s) RETURNING country_id",
                         (country, country_name, continent_id))
            country_id = curs.fetchall()[0]["country_id"]
        else:
            country_id = country_id[0]["country_id"]

        curs.execute("INSERT INTO airport (name, iata, lat, lon, country_id) VALUES (%s, %s, %s, %s, %s)",
                     (name, iata, lat, lon, country_id))

    curs.close()


def insert_job_roles(curs: cursor, job_roles: list, owner_id: int) -> None:
    """Inserts an owners jobs/occupations into db. Expects a cursor object connect to production,
    a list of jobs and the owner id as an int. Returns none."""

    for job_role in job_roles:
        curs.execute("SELECT job_role_id FROM job_role WHERE name = %s", (job_role,))
        job_role_id = curs.fetchall()
        if not job_role_id:
            curs.execute("INSERT INTO job_role (name) VALUES (%s) RETURNING job_role_id", (job_role,))
            job_role_id = curs.fetchall()[0]["job_role_id"]
        else:
            job_role_id = job_role_id[0]["job_role_id"]

        curs.execute("INSERT INTO owner_role_link (owner_id, job_role_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (owner_id, job_role_id))


def get_aircraft_model_id(curs: cursor, aircraft_model: str, aircraft_info: dict[dict]) -> int | None:
    """Returns the id of the aircraft model if it exists in the dataset. Otherwise returns none."""

    if not aircraft_model or aircraft_model not in aircraft_info:
        return None

    aircraft_model_name = aircraft_info[aircraft_model]["name"]
    fuel_efficiency = aircraft_info[aircraft_model]["galph"]

    curs.execute("SELECT model_id FROM model WHERE code = %s", (aircraft_model,))
    model_id = curs.fetchall()
    if model_id:
        return model_id[0]["model_id"]

    curs.execute("INSERT INTO model (code, name, fuel_efficiency) VALUES (%s, %s, %s) RETURNING model_id",
                (aircraft_model, aircraft_model_name, fuel_efficiency))
    return curs.fetchall()[0]["model_id"]


def get_aircraft_owner_id(curs: cursor, name: str, gender_id: int, est_net_worth: int, birthdate: datetime) -> int:
    """Returns the jet owner id if it exists, otherwise inserts a new owner and returns their
    owner id. Expects a cursor object connected to the production db as well as information about
    the owner. Returns an integer."""

    curs.execute("SELECT owner_id FROM owner WHERE name = %s", (name,))
    owner_id = curs.fetchall()
    if owner_id:
        return owner_id[0]["owner_id"]

    curs.execute("""INSERT INTO owner (name, gender_id, est_net_worth, birthdate)
                VALUES (%s, %s, %s, %s) RETURNING owner_id""",
                (name, gender_id, est_net_worth, birthdate))
    return curs.fetchall()[0]["owner_id"]


def get_gender_id(curs: cursor, gender: str) -> int | None:
    """Returns appropriate gender id from db if it exists, otherwise inserts the gender and
    returns the new gender id. Expects a cursor object connected to the production db and the 
    gender as a string. Gender id is an integer."""

    if not gender:
        return None

    curs.execute("SELECT gender_id FROM gender WHERE name = %s", (gender,))
    gender_id = curs.fetchall()
    if gender_id:
        return gender_id[0]["gender_id"]

    curs.execute("INSERT INTO gender (name) VALUES (%s) RETURNING gender_id", (gender,))
    return curs.fetchall()[0]["gender_id"]


def insert_jet_owner_info(conn: connection, aircraft_info: dict[dict], owner_info: list[dict]) -> None:
    """Inserts jet owner data."""

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

        gender_id = get_gender_id(curs, gender)

        owner_id = get_aircraft_owner_id(curs, name, gender_id, est_net_worth, birthdate)

        model_id = get_aircraft_model_id(curs, aircraft_model, aircraft_info)

        curs.execute("INSERT INTO aircraft (tail_number, model_id, owner_id) VALUES (%s, %s, %s)",
                     (tail_number, model_id, owner_id))

        insert_job_roles(curs, job_roles, owner_id)

    curs.close()


def insert_todays_flights(prod_conn: connection, stage_conn: connection,
                          airport_info: dict[dict], aircraft_info: dict[dict]) -> None:
    """Inserts todays flights into the database. Expects a production connection object."""

    curs = prod_conn.cursor(cursor_factory=RealDictCursor)

    for flight in extract_todays_flights(stage_conn):
        tail_number, flight_no, dep_time, dep_location, arr_time, arr_location, emergency = flight

        print(tail_number)
        curs.execute("SELECT * FROM aircraft WHERE tail_number = %s", (tail_number,))
        if not curs.fetchall():
            continue

        dep_airport = find_nearest_airport(*dep_location, airport_info)
        arr_airport = find_nearest_airport(*arr_location, airport_info)
        if dep_airport == arr_airport:
            continue

        curs.execute("SELECT airport_id FROM airport WHERE iata = %s", (dep_airport,))
        dep_airport_id = curs.fetchall()[0]["airport_id"]
        curs.execute("SELECT airport_id FROM airport WHERE iata = %s", (arr_airport,))
        arr_airport_id = curs.fetchall()[0]["airport_id"]

        curs.execute("""SELECT code FROM model JOIN aircraft ON model.model_id = aircraft.model_id
                     WHERE aircraft.tail_number = %s""", (tail_number,))
        aircraft_model = curs.fetchall()
        if aircraft_model:
            aircraft_model = aircraft_model[0]["code"]
            fuel_usage = calculate_fuel_consumption(dep_time, arr_time, aircraft_model, aircraft_info)
        else:
            fuel_usage = None

        if not emergency:
            emergency = "none"
        curs.execute("SELECT emergency_id FROM emergency WHERE type = %s", (emergency,))
        emergency_id = curs.fetchall()
        if not emergency_id:
            curs.execute("INSERT INTO emergency (type) VALUES (%s) RETURNING emergency_id", (emergency,))
            emergency_id = curs.fetchall()[0]["emergency_id"]
        else:
            emergency_id = emergency_id[0]["emergency_id"]

        curs.execute("""INSERT INTO flight (flight_number, dep_airport_id, arr_airport_id, dep_time, arr_time, tail_number,
                     emergency_id, fuel_usage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                     (flight_no, dep_airport_id, arr_airport_id, dep_time, arr_time, tail_number, emergency_id, fuel_usage))

    curs.close()


def handler(event = None, context = None) -> None:
    """AWS lambda handler function that loads in json data, reads from the staging db and
    inserts flights, airports and owners into production db."""

    # Load data sets from S3
    airport_data = clean_airport_data(load_json_file_from_s3(AIRPORTS_JSON, S3_BUCKET_NAME))
    aircraft_data = load_json_file_from_s3(AIRCRAFTS_JSON, S3_BUCKET_NAME)
    jet_owners_data = load_json_file_from_s3(JET_OWNERS_JSON, S3_BUCKET_NAME)

    # Establish db connections
    staging_conn = get_db_connection(STAGING_SCHEMA)
    production_conn = get_db_connection(PRODUCTION_SCHEMA)

    # Insert airport data if it's not already there
    insert_airport_info(production_conn, airport_data)

    # Insert jet owner data if it's not already there or if it's been updated
    insert_jet_owner_info(production_conn, aircraft_data, jet_owners_data)

    # Insert all completed flights from past 24 hours
    insert_todays_flights(production_conn, staging_conn, airport_data, aircraft_data)

    # Commit changes to the dbs
    production_conn.commit()
    staging_conn.commit()

    # Close the db connections
    production_conn.close()
    staging_conn.close()


if __name__ == "__main__":
    handler()
