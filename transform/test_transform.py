from datetime import datetime, timedelta
from transform import *
from utilities import haversine_distance, find_nearest_airport, calculate_fuel_consumption



def test_antipodal_haversine_distance_is_half_circumference_of_earth():
    """"""
    assert round(haversine_distance(-90, 135, 90, -45)) == 20015


def test_haversine_distance_between_same_points_is_zero():
    """"""
    assert haversine_distance(17, 17, 17, 17) == 0


def test_haversine_distance():
    """"""
    assert round(haversine_distance(-18, 35, 72, -40)) == 11407


def test_find_nearest_airport_BER(airport_data):
    """"""
    assert find_nearest_airport(52.36, 13.51, airport_data) == "BER"


def test_find_nearest_airport_WKK(airport_data):
    """"""
    assert find_nearest_airport(59.3, -158.61, airport_data) == "WKK"


def test_fuel_usage_of_LJ40_over_one_hour(aircraft_data):
    """"""
    test_dep_time = datetime.now() - timedelta(hours=1)
    test_arr_time = datetime.now()
    assert calculate_fuel_consumption(test_dep_time, test_arr_time, "LJ40", aircraft_data) == 207


def test_fuel_usage_of_GA5C(aircraft_data):
    """"""
    test_dep_time = datetime.now() - timedelta(hours=7, minutes=42, seconds=87)
    test_arr_time = datetime.now()
    assert round(calculate_fuel_consumption(test_dep_time, test_arr_time, "GA5C", aircraft_data)) == 3105