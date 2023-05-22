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


def test_find_nearest_airport():
    """"""
    assert 0