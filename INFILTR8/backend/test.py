from flask import Flask, make_response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/api/*": {"origins": "*"}})  # Apply CORS to all routes under '/api'
@app.route("/test")
def test():
    # response = make_response()
    #  response.headers.add("Access-Control-Allow-Origin", "*")
    # response.headers.add("Access-Control-Allow-Headers", "*")
    # response.headers.add("Access-Control-Allow-Methods", "*")
    return jsonify({'info': 'test this means flask is working'})