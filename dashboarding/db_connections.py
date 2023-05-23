import pandas as pd
import sqlalchemy as sql
from sqlalchemy.engine.base import Engine
from pandas import DataFrame



class SQLconnection():
    def __init__(self, config:dict) -> None:
        self.table_schema = config["PRODUCTION_SCHEMA"]
        self.host = config["DB_HOST"]
        self.port = config["DB_PORT"]
        self.username = config["DB_USER"]
        self.password = config["DB_PASSWORD"]
        self.db_name = config["DB_NAME"]
        self.engine = self.__create_engine(config["DB_HOST"], config["DB_PORT"], config["DB_USER"], 
                                         config["DB_PASSWORD"], config["DB_NAME"])

    def write_df_to_table(self, data: DataFrame, table_name:str, schema:str, if_exists:str='append'):
        """ Writes a given DataFrame to an SQL table and schema """
        data.to_sql(name=self.table_name, con=self.engine.connect(), schema=self.table_schema,
                    if_exists=if_exists, index=False)


    def __create_engine(self, host,port, username, password, db_name) -> Engine:
        """ Creates a DB engine from .env parameters """
        return sql.create_engine(f'postgresql://{username}:{password}@{host}/{db_name}')


def get_data_as_dataframe(sql: SQLconnection, table:str) -> DataFrame:
    return pd.read_sql_table(table_name=table, con=sql.engine.connect(), schema=sql.table_schema)
