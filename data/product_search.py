
import psycopg2
from psycopg2 import sql
import json
from decimal import Decimal
from datetime import datetime
import configparser

# Read database configuration from config.ini
config = configparser.ConfigParser()
config.read('../ini/config.ini')

host = config['database_config']['host']
database = config['database_config']['database']
user = config['database_config']['user']
password = config['database_config']['password']


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomEncoder, self).default(obj)
    

def connect_to_database():
    try:
        # Connect to PostgreSQL database
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        return connection
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
        return None

def query_table(table_name, query):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        
        # Execute the query
        cursor.execute(sql.SQL(query).format(sql.Identifier(table_name)))
        
        # Fetch all rows from the executed query
        rows = cursor.fetchall()
         
        # Convert rows to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        
        # Convert list of dictionaries to JSON
        json_result = json.dumps(result, indent=4, cls=CustomEncoder)
        
        # Print the JSON result
        #print(json_result)
        if connection:
            cursor.close()
            connection.close()
            #print("PostgreSQL connection is closed")
        return json_result
        
    except psycopg2.Error as error:
        print("Error while querying PostgreSQL table", error)
    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()
            #print("PostgreSQL connection is closed")


def search_product(search_string, price_filter):
    table_name = "products"
    product_query_filter = f"%{search_string}%"   
    query = f"SELECT * FROM {{}} WHERE name LIKE '{product_query_filter}' AND price >= {price_filter}"
    product_search_result = query_table(table_name, query)
    return product_search_result