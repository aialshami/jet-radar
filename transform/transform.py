import json
from math import sin, cos, acos, asin, sqrt, pi


AIRPORTS_JSON_FILE_PATH = "./airports.json"
AIRCRAFT_FUEL_CONSUMPTION_JSON_FILE_PATH = "./aircraft_fuel_consumption_rates.json"


def load_airport_locations(data_file_path: str = AIRPORTS_JSON_FILE_PATH) -> dict:
    """Returns a dictionary with airport codes as keys and the location of the 
    airport in a latitude, longitude tuple as values. Expects a file path as input."""

    with open(data_file_path) as f:
        airport_data = json.load(f)

    return {airport["iata"]: (float(airport["lat"]), float(airport["lon"]))
            for airport in airport_data 
            if "lat" in airport and "lon" in airport}


def load_aircraft_fuel_consumption_rates(data_file_path: str = AIRCRAFT_FUEL_CONSUMPTION_JSON_FILE_PATH) -> dict:

    with open(data_file_path) as f:
        aircraft_data = json.load(f)


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
    """Finds closest airport to input latitude and longitude and returns the airport IATA code as a string.
    Expects latitude and longitude as floats and a dictionary of airport locations."""

    return sorted(airport_locations.items(), key=lambda x: haversine_distance(*x[1], lat, lon))[0][0]


if __name__ == "__main__":

    airport_locations = load_airport_locations()
    print(find_nearest_airport(52, 13.7, airport_locations))