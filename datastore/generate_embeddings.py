import psycopg2
from openai import OpenAI
import sys
import os
import certifi



# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
from product_search import connect_to_database
import time

#print(certifi.where())
# get the python certificate path by using the below command - python3 -m certifi
os.environ['REQUESTS_CA_BUNDLE'] = '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/certifi/cacert.pem'

client = OpenAI()

connection = connect_to_database()


def query_table(query):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query)
        
        # Fetch all rows from the executed query
        rows = cursor.fetchall()
         
        # Convert rows to list of dictionaries
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]
        
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
    
def update_embeddings():

    # Query the recipes table
    recipes = query_table("SELECT rid, recipe_name, cuisine_path, ingredients, nutrition, directions FROM recipes")
    count = 0
    # Generate embeddings for each recipe
    for recipe in recipes:
        recipe_name = recipe['recipe_name']
        ingredients = recipe['ingredients']
        nutrition = recipe['nutrition']
        directions = recipe['directions']
        rid = recipe['rid']
        
        # Concatenate the fields
        combined_text = f"{recipe_name} {ingredients} {nutrition} {directions}"
        
        # Generate a single embedding for the concatenated text
        combined_embedding = generate_embeddings(combined_text)
        
        # Update the recipes table with the embeddings
        try:
            connection = connect_to_database()
            cursor = connection.cursor()
            query = "UPDATE recipes SET embedding = %s WHERE rid = %s"
            cursor.execute(query, (combined_embedding, rid))
            print("updated the embedding %s for recipe id %s ", combined_embedding, rid)
            print("Updated %s records", count)
            print("waiting for 1 second to avoid the rate limit error")
            time.sleep(1)
            count = count+1
            connection.commit()
        except psycopg2.Error as error:
            print("Error while updating PostgreSQL table", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
        
    print("Embeddings generated and updated in the recipes table")

update_embeddings()
