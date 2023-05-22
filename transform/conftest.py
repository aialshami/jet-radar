import pytest
from transform import load_json_file_from_s3, AIRPORTS_JSON, AIRCRAFTS_JSON
from utilities import clean_airport_data


@pytest.fixture
def airport_data():
    return clean_airport_data(load_json_file_from_s3(AIRPORTS_JSON))


@pytest.fixture
def aircraft_data():
    return load_json_file_from_s3(AIRCRAFTS_JSON)