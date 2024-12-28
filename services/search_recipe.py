import os
import sys
from flask import Flask, request, jsonify

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

from recipe_search import sem_search_recipe

app = Flask(__name__)

@app.route('/search_recipe', methods=['GET'])
def search_recipe():
    recipe_query = request.args.get('recipe')
    if not recipe_query:
        return jsonify({"error": "No recipe query provided"}), 400

    # Here you would add your logic to search for the recipe
    # For now, we'll just return the query as a placeholder
    result = sem_search_recipe(recipe_query)

    return result

if __name__ == '__main__':
    app.run(debug=True)