from flask import Blueprint, jsonify, request
from app import db
from dotenv import load_dotenv
import os
import requests

weather = Blueprint('weather', __name__, url_prefix="/destination")

@weather.route("/weather", methods=['GET'])
def get_weather():
    city = request.args.get('city')
    country = request.args.get('country')
    if not city:
        return jsonify({'error': 'City is required'}), 400

    # Construct the query with optional country
    query = f"{city},{country}" if country else city
    
    openweather_api_key = os.environ.get('OPENWEATHER_API_KEY') 
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={query}&cnt=7&appid={openweather_api_key}'
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch weather data'}), response.status_code

    return jsonify(response.json())