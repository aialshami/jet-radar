import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection
from dotenv import load_dotenv
import pandas as pd
import os


load_dotenv()
config = os.environ


def get_db_connection() -> connection:
    """Establishes connection to database. Returns psycopg2 connection object."""

    return psycopg2.connect(user = config["DATABASE_USERNAME"],
                            password = config["DATABASE_PASSWORD"],
                            host = config["DATABASE_IP"],
                            port = config["DATABASE_PORT"],
                            database = config["DATABASE_NAME"],
                            options = "-c search_path=staging")


if __name__ == "__main__":
    
    conn = get_db_connection()
    print(conn)

    df = pd.read_sql("SELECT * FROM tracked_event;", conn)
    print(df)

    flight_numbers = df["aircraft_reg"].unique()
    for flight_no in flight_numbers:
        flight = df[df["aircraft_reg"] == flight_no].sort_values("time_input").reset_index().to_dict('records')

        num_of_events = len(flight)
        if num_of_events == 1:
            continue
        seconds_since_last_event = (pd.Timestamp.now() - flight[-1]["time_input"]).total_seconds()
        if seconds_since_last_event < 30*60:
            continue

        first_event = flight[0]
        dep_time = first_event["time_input"]
        dep_location = (first_event["lat"], first_event["lon"])

        for i in range(1, num_of_events):
            current_event = flight[i]
            previous_event = flight[i-1]
            event_gap = (current_event["time_input"] - previous_event["time_input"]).total_seconds()

            if event_gap < 60*60 and i != num_of_events-1:
                continue
            elif i == num_of_events-1:
                arr_time = current_event["time_input"]
                arr_location = (current_event["lat"], current_event["lon"])
                # yield stuff
            else:
                arr_time = previous_event["time_input"]
                arr_location = (previous_event["lat"], previous_event["lon"])
                # yield stuff
                dep_time = current_event["time_input"]
                dep_location = (current_event["lat"], current_event["lon"])
