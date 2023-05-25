import numpy as np
import pandas as pd

from pandas import DataFrame
from datetime import datetime
from math import floor



CELEB_DROPDOWN_OPTIONS=[{"label": "Elon Musk", "value": "elon_musk",}, {"label": "Tom Cruise", "value": "tom_cruise",},
                        {"label": "Oprah Winfrey","value": "oprah_winfrey",}, {"label": "Floyd Mayweather", "value": "floyd_mayweather",},
                        {"label": "Taylor Swift", "value": "taylor_swift",}, {"label": "Bill Gates", "value": "bill_gates",},
                        {"label": "Kim Kardashian", "value": "kim_kardashian",}, {"label": "Travis Scott", "value": "travis_scott",},
                        {"label": "Kylie Jenner", "value": "kylie_jenner",}, {"label": "Donald Trump", "value": "donald_trump",},
                        {"label": "Jim Carrey", "value": "jim_carrey",}, {"label": "John Travolta", "value": "john_travolta",},
                        {"label": "Jay-Z", "value": "jay_z",}, {"label": "Steven Spielberg", "value": "steven_spielberg",}, 
                        {"label": "Mark Wahlberg", "value": "mark_wahlberg",}, {"label": "A-Rod", "value": "a_rod",},
                        ]

CO2_PER_GALLON = 0.01 #mtCO2 i.e metric tons of co2
AVG_CO2_COMMUTE = 0.00496 #mtCo2 src: https://www.climatepartner.com/en/news/how-sustainable-commuting-can-improve-a-company-carbon-footprint#:~:text=Due%20to%20its%20significant%20impact,per%20commuting%20employee%20per%20day.
AVG_FUEL_COST = 5.91 #https://www.airnav.com/fuel/report.html


def get_age_from_birthdate(birthdate: np.datetime64) -> int:
    """ Converts stored birthdate to numerical age (initially yyyy-mm-dd) """
    if isinstance(birthdate, np.datetime64):
        unix_epoch = np.datetime64(0, 's')
        seconds_since_epoch = (birthdate - unix_epoch) / np.timedelta64(1, 's')
        birthdate = datetime.utcfromtimestamp(seconds_since_epoch)
        return floor((datetime.now()-birthdate).days/365)

    elif isinstance(birthdate, str) and '-' in birthdate:
        separated_by_dash = birthdate.split('-')
        year = int(separated_by_dash[0])
        month = int(separated_by_dash[1])
        day = int(separated_by_dash[2]) 
        return floor((datetime.now()-datetime(year, month, day)).days/365)
    else:
        raise ValueError("Birthdate not in a correct format")


def get_gender_from_id(gender_id:int, gender_df: DataFrame) -> str:
    """ Maps gender_id to gender """
    gender_row = gender_df[gender_df["gender_id"] == gender_id]
    return gender_row["name"].values[0]


def get_most_recent_flight_info(owner:DataFrame, flight_df: DataFrame, aircraft_df:DataFrame, airport) -> dict:
    """ For a given person return the useful data of the most recent flight they've completed.
        In progress flights will not appear until the next running of prod. Lambda.
    """
    owner_aircraft_df = pd.merge(owner, aircraft_df, on="owner_id")
    flight_merge_df = pd.merge(flight_df, owner_aircraft_df, on="tail_number")
    combined_df = pd.merge(flight_merge_df, airport, left_on= "dep_airport_id", right_on="airport_id", suffixes=("_owner","_dep_airport"))
    combined_df = pd.merge(combined_df, airport, left_on= "arr_airport_id", right_on="airport_id", suffixes=("_dep_airport","_arr_airport"))

    fuel_df = combined_df.filter([
        "fuel_usage","lat_dep_airport","lon_dep_airport",
        "lat_arr_airport","lon_arr_airport", "dep_time", "arr_time"]).head(5)

    return fuel_df.to_dict()


def manage_names_with_dashes(name:str) -> str:
    """ Converts names that should have dashes, plus A-rod """
    if name.lower() == "jay z":
        return name.replace(" ", "-")
    elif name.lower() =="a rod":
        return "A-rod"
    else:
        return name

def get_celeb_info(name: str, owner_df:DataFrame, gender_df:DataFrame) -> list[str]:
    """Return the name/gender/age/worth with prefix attached """
    name = manage_names_with_dashes(name)

    owner_record = owner_df[owner_df["name"] == name] # gets the owner id for this celeb
    gender = get_gender_from_id(int(owner_record['gender_id'].values[0]), gender_df)

    age = str(get_age_from_birthdate(owner_record["birthdate"].values[0]))
    worth = str(round(owner_record["est_net_worth"].values[0]/10**6)) + " M"

    return [name, gender, age, worth]


def get_flight_cost(gallons:float) -> float:
    """ Gives the cost of the flight in dollars """
    return round(AVG_FUEL_COST * gallons,2)

def get_flight_co2(gallons:float) -> float:
    """ Returns the co2 output of a flight """
    return round(CO2_PER_GALLON * gallons, 2)

def get_flight_time(departure, arrival) -> str:
    """ Get the flight time from the flight data """
    num_hrs = floor((arrival.to_pydatetime() - departure.to_pydatetime()).seconds/(3600))
    num_mins = int((arrival.to_pydatetime() - departure.to_pydatetime()).seconds/(60)) - num_hrs*60
    
    return f"{num_hrs} hrs, {num_mins} mins", (arrival.to_pydatetime() - departure.to_pydatetime()).seconds/3600



def get_total_number_of_flights(name:str, owner_df:DataFrame, aircraft_df: DataFrame, flight_df:DataFrame) -> str:
    """ Gets the total number of flights we've tracked for celeb w/ given name """
    name = manage_names_with_dashes(name)

    owner_record = owner_df[owner_df["name"] == name] # gets the owner id for this celeb
    owner_aircraft = aircraft_df[aircraft_df["owner_id"] == owner_record["owner_id"].values[0]]
    relevant_flights = flight_df[flight_df["tail_number"] == owner_aircraft["tail_number"].values[0]]
    return "# of flights tracked is: " + str(len(relevant_flights))


def get_new_infographic_text(comparison: str, value:float) -> str:
    """ Changes the infographic text to the next visualisation emoji prompt """
    if comparison == "co2":
        quantity, item, emoji = compare_co2(value)
        return f"This flight is equivalent to {quantity} {item}s of CO2 {emoji}"
    elif comparison == "cost":
        quantity, item, emoji = compare_cost(value)
        return f"This flight is equivalent to the cost of {quantity} {item}s {emoji}"
    elif comparison == "fuel":
        quantity, item, emoji = compare_fuel(value)
        return f"This flight is equivalent to the fuel of {quantity} {item}s {emoji}"
    elif comparison == "time":
        quantity, item, emoji = compare_time(value)
        return f"This flight is equivalent to the time of {quantity} {item}s {emoji}"


UNICODE = {"cow": "\U0001F42E", "car": "\U0001F697", "plane": "\U0001F6E9", 
           "tree": "\U0001F333", "football": "\U000026BD", "album":"\U0001F3B5", 
           "phone": "\U0001F4F1", "film":"\U0001F3A5", "sweets":"\U0001F36C", 
           "shopping": "\U0001F6D2", "tea":"\U00002615", "beer": "\U0001F37A"}

# CO2 is yrly, cost is avg per item, fuel is in gal, time in hrs
COMPARISONS = {"co2": {"tree": 0.167, "cow": 2.5, "car": 2.58},
               "cost": {"phone": 208, "sweets": 1.88, "shopping": 106.64},
               "fuel": {"tea": 0.0264172, "beer": 0.01501},
               "time": {"film": 1.68, "album": 0.73, "football": 1.5}}


def compare_co2(amount:float) -> tuple[int, str, str]:
    """ Gets a random comparison for the mtCO2 of the flight """
    random_comp = np.random.choice(list(COMPARISONS["co2"].keys()))
    comp_value = COMPARISONS["co2"][random_comp]
    return round(amount/comp_value,1), random_comp, UNICODE[random_comp]

def compare_cost(amount:float) -> tuple[int, str, str]:
    """ Gets a random comparison for the mtCO2 of the flight """
    random_comp = np.random.choice(list(COMPARISONS["cost"].keys()))
    comp_value = COMPARISONS["cost"][random_comp]
    return round(amount/comp_value,1), random_comp, UNICODE[random_comp]

def compare_fuel(amount:float) -> tuple[int, str, str]:
    """ Gets a random comparison for the mtCO2 of the flight """
    random_comp = np.random.choice(list(COMPARISONS["fuel"].keys()))
    comp_value = COMPARISONS["fuel"][random_comp]
    return round(amount/comp_value, 1), random_comp, UNICODE[random_comp]

def compare_time(amount:float) -> tuple[int, str, str]:
    """ Gets a random comparison for the mtCO2 of the flight """
    random_comp = np.random.choice(list(COMPARISONS["time"].keys()))
    comp_value = COMPARISONS["time"][random_comp]
    return round(amount/comp_value,1), random_comp, UNICODE[random_comp]


