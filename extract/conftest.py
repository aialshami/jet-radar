"""Conftest file for extract module tests."""
import os
import json
import pytest


def clean_airport_data(airport_info: list[dict]) -> dict[dict]:
    """Removes airports that don't have latitude, longitude and iata information. Expects a list of dicts
    and returns the filtered list."""

    return {airport["iata"]: airport for airport in airport_info
            if "lat" in airport and "lon" in airport and "iata" in airport}


def load_json_from_data_directory(file_name: str) -> dict | list:
    """Loads a json file from the data directory and returns it as a python
    object. Expects a file name as a string."""

    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, f"../data/{file_name}")

    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture
def airport_data() -> dict[dict]:
    """Returns airports data as a dict of dicts."""
    return clean_airport_data(load_json_from_data_directory("airports.json"))


@pytest.fixture
def aircraft_data() -> dict[dict]:
    """Returns aircraft data as dict of dicts."""
    return load_json_from_data_directory("aircraft_fuel_consumption_rates.json")


@pytest.fixture
def celeb_planes_data() -> list[dict]:
    """Returns celeb planes data as a list of dictionaries."""
    return load_json_from_data_directory("celeb_planes.json")
