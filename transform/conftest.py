import pytest
import os
import json

from transform import load_json_file_from_s3, AIRPORTS_JSON, AIRCRAFTS_JSON, get_db_connection, STAGING_SCHEMA, \
PRODUCTION_SCHEMA
from utilities import clean_airport_data


def load_json_from_data_directory(file_name: str) -> dict | list:
    """Loads a json file from the data directory and returns it as a python
    object. Expects a file name as a string."""

    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, f"../data/{file_name}")

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def airport_data():
    return clean_airport_data(load_json_from_data_directory("airports.json"))


@pytest.fixture
def aircraft_data():
    return load_json_from_data_directory("aircraft_fuel_consumption_rates.json")
