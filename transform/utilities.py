"""This module contains utility function for calculating the fuel consumption of an aircraft, calculating
Haversine distances and finding nearest airports based on longitude and latitude."""
from math import sin, cos, acos, pi
from datetime import datetime


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


def clean_airport_data(airport_info: list[dict]) -> dict[dict]:
    """Removes airports that don't have latitude, longitude and iata information. Expects a list of dicts
    and returns the filtered list."""

    return {airport["iata"]: airport for airport in airport_info
            if "lat" in airport and "lon" in airport and "iata" in airport}


def find_nearest_airport(lat: float, lon: float, airport_info: list[dict]) -> str:
    """Finds closest airport to input latitude and longitude and returns the airport IATA code and
    location. Expects latitude and longitude as floats and a dictionary of airport locations."""

    return sorted(airport_info.items(),
                  key=lambda x: haversine_distance(float(x[1]["lat"]), float(x[1]["lon"]), lat, lon))[0][0]


def calculate_fuel_consumption(dep_time: datetime, arr_time: datetime, aircraft_model: str,
                               aircraft_info: dict[dict]) -> float:
    """Calculates fuel consumption by multiplying the flight duration in hours by the estimated 
    fuel consumption of the aircraft. Returns this as a float in gallons (galph = gallons per hour). 
    Expects departure/arrival times as datetimes, the aircraft model code and aircraft info.
    """

    flight_duration_hours = (arr_time - dep_time).seconds / 60**2
    fuel_consumption_rate = aircraft_info[aircraft_model]["galph"]

    return flight_duration_hours * fuel_consumption_rate




if __name__ == "__main__":
    pass