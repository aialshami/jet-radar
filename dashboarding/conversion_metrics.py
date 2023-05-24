from pandas import DataFrame
import pandas as pd
from datetime import datetime
from math import floor
import numpy as np
from numpy import random


CELEB_DROPDOWN_OPTIONS=[{"label": "Elon Musk", "value": "elon_musk",}, {"label": "Tom Cruise", "value": "tom_cruise",},
                        {"label": "Oprah Winfrey","value": "oprah_winfrey",}, {"label": "Floyd Mayweather", "value": "floyd_mayweather",},
                        {"label": "Taylor Swift", "value": "taylor_swift",}, {"label": "Bill Gates", "value": "bill_gates",},
                        {"label": "Kim Kardashian", "value": "kim_kardashian",}, {"label": "Travis Scott", "value": "travis_scott",},
                        {"label": "Kylie Jenner", "value": "kylie_jenner",}, {"label": "Donald Trump", "value": "donald_trump",},
                        {"label": "Jim Carrey", "value": "jim_carrey",}, {"label": "John Travolta", "value": "john_travolta",},
                        {"label": "Jay-Z", "value": "jay_z",}, {"label": "Steven Spielberg", "value": "steven_spielberg",}, 
                        {"label": "Mark Wahlberg", "value": "mark_wahlberg",}, {"label": "A-Rod", "value": "a_rod",},
                        ]

UNICODE = {"cow": "\U0001F42E", "car": "\U0001F697", "plane": "\U0001F6E9", 
           "tree": "\U0001F333", "sun": "\U0001F324", "football": "\U000026BD",
           "watch":"\U000023F1", "music":"\U0001F3B5", "phone": "\U0001F4F1",
           "money":"\U0001F4B0", "film":"\U0001F3A5", "sweets":"\U0001F36C", 
           "shopping": "\U0001F6D2", "tea":"\U00002615", "beer": "\U0001F37A"}

co2_per_gallon_fuel = 0.01 #mtCO2 i.e metric tons of co2
AVG_CO2_COMMUTE = 0.00496 #mtCo2 src: https://www.climatepartner.com/en/news/how-sustainable-commuting-can-improve-a-company-carbon-footprint#:~:text=Due%20to%20its%20significant%20impact,per%20commuting%20employee%20per%20day.

def infographic_co2(metric_ton_co2: float) -> str:
    """ Converts the CO2 of a flight to a an infographic metric """
    metric = random.choice(['commute', "trees", "normal_flights"])

    if metric == "commute":
        return "commute"
    elif metric == "trees":
        return "trees"
    elif metric == "normal_flights":
        return "comapre to commercial flights"
    else:
        raise ValueError("Something went seriously wrong with the random")



def get_age_from_birthdate(birthdate: str) -> int:
    """ Converts stored birthdate to numerical age (initially yyyy-mm-dd)"""
    if isinstance(birthdate, str) and '-' in birthdate:
        separated_by_dash = birthdate.split('-')
        year = int(separated_by_dash[0])
        month = int(separated_by_dash[1])
        day = int(separated_by_dash[2]) 
        return floor((datetime.now()-datetime(year, month, day)).days/365)

    elif isinstance(birthdate, np.datetime64):
        unix_epoch = np.datetime64(0, 's')
        seconds_since_epoch = (birthdate - unix_epoch) / np.timedelta64(1, 's')
        birthdate = datetime.utcfromtimestamp(seconds_since_epoch)

        return floor((datetime.now()-birthdate).days/365)
    else:
        raise ValueError("Birthdate not in the correct format")


def get_gender_from_id(gender_id:float, gender_df: DataFrame) -> str:
    """ Maps gender_id to gender """
    gender_row = gender_df[gender_df["gender_id"] == gender_id]
    return gender_row["name"].values[0]


def get_net_worth_as_million_dollars(worth: int) -> str:
    """ Returns net worth as N millions (i.e 180 *10^6 -> 180M) """
    return f"${round(worth/10**6)}M"


def get_most_recent_flight_info(owner:DataFrame, flights: DataFrame, aircraft:DataFrame) -> dict:
    """ For a given person return the useful data of the most recent flight they've completed.
        In progress flights will not appear until the next running of prod. Lambda
    """
    
    output_dict = {"flight_id":None, "fuel_usage":None, "flight_cost":None, "flight_co2": None, 
                   "start":None, "end": None, "time_taken": None}

    combined_df = pd.merge(flights, aircraft, on='tail_number')
    owners_flights = combined_df[combined_df['owner_id'] == owner["owner_id"].values[0]]
    sorted_flights = owners_flights.sort_values(by='arr_time', ascending=False)

    if not sorted_flights.empty:
        most_recent = sorted_flights[0]
        output_dict["flight_id"] = most_recent[""]
