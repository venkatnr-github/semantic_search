
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))

from product_search import search_product
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_product_endpoint():
    product_name = request.args.get('product_name')
    price = request.args.get('price')
    #print(product_name)
    if not product_name :
        return jsonify({"error": "Product Name parameter is required"}), 400
    if not price:
        price = 0
    result = search_product(product_name, price)
    return result

#if __name__ == '__main__':
app.run(debug=False)


#\copy products("id","name","img","asin","price","mrp","rating","ratingtotal","discount","seller","purl") FROM './products.csv' DELIMITER ',' CSV HEADER;