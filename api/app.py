from flask import Flask, jsonify, request
from reviews import get_reviews

app = Flask(__name__)

@app.route('/')
def index():
    return 'Amazon reviews'

@app.route('/reviews', methods=['POST'])
def reviews():
    data = request.form
    page = 1
    if 'asin' in data and 'country' in data:
        asin = data['asin']
        country = data['country']
        if 'page' in data:
            page = data['page']
        return jsonify(get_reviews(asin, country, page))
    else:
        return jsonify({'Error': 'Asin and Country not provided'})


if __name__== "__main__":
    app.run('0.0.0.0', debug=True)