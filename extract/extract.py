""" This module runs the extraction process for the celebrity plane current flight data """
import os, json, requests, boto3
import pandas as pd

from pandas import DataFrame
from datetime import datetime
from dotenv import load_dotenv
from db_connection import push_to_staging_database


load_dotenv()
config=os.environ


def get_celeb_json() -> dict:
    """ Function for getting the celebrity information from our storage """
    s3_bucket = boto3.resource('s3')

    obj = s3_bucket.Object(config["S3_BUCKET_NAME"], config["CELEB_INFO"])
    celeb_json = json.load(obj.get()['Body'])
    return celeb_json


def get_current_flight_for_icao(icao_number: str) -> json:
    """ Interacts with ADSB-exchange API to get current flight info w/ given ICAO """

    url = f"https://adsbexchange-com1.p.rapidapi.com/v2/icao/{icao_number}/"
    headers = {
        "X-RapidAPI-Key": config["RAPIDAPI_KEY"],
        "X-RapidAPI-Host": config["RAPIDAPI_HOST"]
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_flights_for_all_celebs(celebs: list[dict]) -> list[dict]:
    """ For each celeb, find current flight information by ICAO number """
    data_to_append = []

    for celeb_plane in celebs:
        icao = celeb_plane["icao_hex"].lower()
        current_flight_info = get_current_flight_for_icao(icao)
        data_to_append.append(current_flight_info)
    return data_to_append


def convert_flight_list_to_df(flights:list[dict]) -> DataFrame:
    """ Converts the acquired list into a dataframe to easily put it into staging DB """

    flight_list = []
    for flight in flights:
        # #i.e if plane is in the air, add flight details in appropriate format
        if flight["ac"] != []:
            flight_list.append(get_flight_params(flight))
    return pd.DataFrame(flight_list)


def get_flight_params(flight: dict) -> list:
    """ extracts staging data from API info """
    flight_data:dict = {}

    flight_info = flight["ac"][0]
    flight_data["time_input"] = datetime.utcfromtimestamp(flight["now"]/1000)
    
    for key in flight_info.keys():
        if key == "flight":
            flight_data["flight_no"] = flight_info["flight"]
        elif key == "r":
            flight_data["aircraft_reg"] = flight_info["r"]
        elif key == "t":
            flight_data["model"] = flight_info["t"]
        elif key == "alt_baro":
            flight_data["barometric_alt"] = flight_info["alt_baro"]
        elif key == "alt_geom":
            flight_data["geometric_alt"] = flight_info["alt_geom"]
        elif key == "gs":
            flight_data["ground_speed"] = flight_info["gs"]
        elif key == "track":
            flight_data["true_track"] = flight_info["track"]
        elif key == "baro_rate":
            flight_data["barometric_alt_roc"] = flight_info["baro_rate"]
        elif key == "emergency":
            flight_data["emergency"] = flight_info["emergency"]
        elif key == "lat":
            flight_data["lat"] = flight_info["lat"]
        elif key == "lon":
            flight_data["lon"] = flight_info["lon"]

    return flight_data


def handler(event, context) -> None:
    """ The handler function to execute the extraction process """
    # Pulls celeb info from S3
    celeb_json = get_celeb_json()

    # Gets a list of current flight data for each celeb
    flight_data = get_flights_for_all_celebs(celeb_json)

    # Converts the data to df
    flight_df = convert_flight_list_to_df(flight_data)

    # Pushes to staging DB
    push_to_staging_database(config, flight_df)

    return flight_df.to_json()
