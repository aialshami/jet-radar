import json


AIRPORTS_JSON_FILE_PATH = "./airports.json"


def load_airport_locations(data_file_path: str = AIRPORTS_JSON_FILE_PATH) -> dict:
    """Returns a dictionary with airport codes as keys and the location of the 
    airport in a latitude, longitude tuple as values. Expects a file path as input."""

    with open(data_file_path) as f:
        airport_data = json.load(f)

    return {airport["iata"]: (float(airport["lat"]), float(airport["lon"]))
            for airport in airport_data 
            if "lat" in airport and "lon" in airport}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    pass


def find_nearest_airport(lat: float, lon: float, airport_locations: dict):
    pass


if __name__ == "__main__":

    print(load_airport_locations())