import pytest
from transform import load_json_file_from_s3, AIRPORTS_JSON, AIRCRAFTS_JSON, get_db_connection, STAGING_SCHEMA, \
PRODUCTION_SCHEMA
from utilities import clean_airport_data


@pytest.fixture
def airport_data():
    return clean_airport_data(load_json_file_from_s3(AIRPORTS_JSON))


@pytest.fixture
def aircraft_data():
    return load_json_file_from_s3(AIRCRAFTS_JSON)


@pytest.fixture
def staging_db_connection():
    return get_db_connection(STAGING_SCHEMA)


@pytest.fixture
def production_db_connection():
    return get_db_connection(PRODUCTION_SCHEMA)