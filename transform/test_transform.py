"""Tests for transform module and it's utility functions."""
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor
import pandas as pd

from utilities import haversine_distance, find_nearest_airport, calculate_fuel_consumption
from transform import extract_todays_flights


def test_antipodal_haversine_distance_is_half_circumference_of_earth():
    """Check that Haversine distance between the poles is equal to half the
    circumference of the earth."""

    assert round(haversine_distance(-90, 135, 90, -45)) == 20015


def test_haversine_distance_between_same_points_is_zero():
    """Check that the Haversine distance between a point and itself is 0."""

    assert haversine_distance(17, 17, 17, 17) == 0


def test_haversine_distance():
    """Test the Haversine distance between two points."""

    assert round(haversine_distance(-18, 35, 72, -40)) == 11407


def test_find_nearest_airport_ber(airport_data):
    """Checks that when the lat/lon of BER is input to the find_nearest_airport
    function, BER is returned."""

    assert find_nearest_airport(52.36, 13.51, airport_data) == "BER"


def test_find_nearest_airport_wkk(airport_data):
    """Checks that when the lat/lon of WKK is input to the find_nearest_airport
    function, WKK is returned."""

    assert find_nearest_airport(59.3, -158.61, airport_data) == "WKK"


def test_fuel_usage_of_lj40_over_one_hour(aircraft_data):
    """Tests the fuel usage of LJ40 jet over a single hour."""

    test_dep_time = datetime.now() - timedelta(hours=1)
    test_arr_time = datetime.now()
    assert calculate_fuel_consumption(test_dep_time, test_arr_time, "LJ40", aircraft_data) == 207


def test_fuel_usage_of_ga5c(aircraft_data):
    """Tests the fuel usage of GA5C jet over 7 hours 43 minutes and 27 seconds."""

    test_dep_time = datetime.now() - timedelta(hours=7, minutes=42, seconds=87)
    test_arr_time = datetime.now()
    assert round(calculate_fuel_consumption(test_dep_time, test_arr_time, "GA5C", aircraft_data)) == 3105


@patch('pandas.read_sql')
def test_extract_flights_creates_cursor(mock_read):
    """Checks that a cursor is created and cursor execute is called."""

    mocked_db_connection = MagicMock()
    mocked_cursor = mocked_db_connection.cursor
    mocked_cursor_execute = mocked_cursor.return_value.execute

    mocked_df = pd.DataFrame({"aircraft_reg": [1], "flight_no": [1], "time_input": [datetime.now()-timedelta(hours=3)],
                              "lat": [1], "lon": [1], "emergency": [None]})
    mock_read.return_value = mocked_df

    extract_todays_flights(mocked_db_connection)

    mocked_cursor.assert_called_with(cursor_factory=RealDictCursor)
    mocked_cursor_execute.assert_called()
