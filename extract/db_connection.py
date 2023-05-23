""" This module is responsible for sending collected data to the staging DB """
import sqlalchemy as sql
from sqlalchemy.engine.base import Engine
from pandas import DataFrame

class SQL():
    """ This holds the interaction with the DB for ease of use """
    def __init__(self, config:dict) -> None:
        self.host = config["DB_HOST"]
        self.port = config["DB_PORT"]
        self.username = config["DB_USER"]
        self.password = config["DB_PASSWORD"]
        self.db_name = config["DB_NAME"]
        self.engine = self.create_engine(config["DB_HOST"], config["DB_USER"],
                                         config["DB_PASSWORD"], config["DB_NAME"])

    def write_df_to_table(self, data: DataFrame, table:str, schema:str, if_exists:str='append'):
        """ Writes a given DataFrame to an SQL table and schema """
        data.to_sql(name=table, con=self.engine.connect(), schema=schema,
                    if_exists='append', index=False)


    def create_engine(self, host, username, password, db_name) -> Engine:
        """ Creates a DB engine from .env parameters """
        return sql.create_engine(f'postgresql://{username}:{password}@{host}/{db_name}')



def push_to_staging_database(config: dict, data: DataFrame):
    """ Create staging DB if not exists, then push 
        combined data file to staging DB 
    """
    sql_conn = SQL(config)
    table, schema = config["STAGING_TABLE_NAME"], config["STAGING_SCHEMA"]
    sql_conn.write_df_to_table(data=data, table=table, schema=schema)