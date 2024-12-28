# Read database configuration from config.ini
import ast
import configparser
from datetime import datetime
from decimal import Decimal
import json
import os

from openai import OpenAI
import psycopg2
from torch import cosine_similarity
import torch
os.environ['REQUESTS_CA_BUNDLE'] = '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/certifi/cacert.pem'

client = OpenAI()

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

def query_table(query):
    try:
        connection = connect_to_database()
        if connection is None:
            return []
        
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        # Convert rows to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
            
        # Parse the embedding strings into lists of floats
        for row in result:
            if 'embedding' in row:
                row['embedding'] = ast.literal_eval(row['embedding'])
            
        return result
    except psycopg2.Error as error:
        print("Error while querying PostgreSQL table", error)
        return None
    finally:
        if connection:
            cursor.close()
            connection.close()
   

def generate_embeddings(text):
    embedding = client.embeddings.create(
        input=text,
        model="text-embedding-3-large",
    )
    
    embedding_value = embedding.data[0].embedding
    return embedding_value

def sem_search_recipe(recipe):
    # Generate embeddings for the input recipe
    recipe_embedding = generate_embeddings(recipe)
    
    # Query the recipes table
    recipes = query_table("SELECT rid, recipe_name, cuisine_path, ingredients, nutrition, directions, embedding FROM recipes")
    similarity_scores = []
    for db_recipe in recipes:
        db_embedding = db_recipe['embedding']
        similarity = cosine_similarity(torch.tensor(recipe_embedding).unsqueeze(0), torch.tensor(db_embedding).unsqueeze(0))
        similarity_scores.append((db_recipe['rid'], db_recipe['recipe_name'], similarity))
    
    # Sort by similarity score in descending order
    similarity_scores.sort(key=lambda x: x[2], reverse=True)
    
    # Extract the recipe values from similarity_scores
    top_recipes = []
    for score in similarity_scores[:10]:
        recipe_id = score[0]
        recipe_name = score[1]
        similarity = score[2].item()  # Convert tensor to float
        top_recipes.append({
            'recipe_id': recipe_id,
            'recipe_name': recipe_name,
            'similarity': similarity
        })
    
    # Return the top 10 most similar recipes
    results = json.dumps(top_recipes, cls=CustomEncoder)
    return results


#print(sem_search_recipe("chicken curry"))