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


    geocoding_url = f'http://api.openweathermap.org/data/2.5/weather?q={query}&appid={openweather_api_key}'
    geocoding_response = requests.get(geocoding_url)

    if geocoding_response.status_code != 200:
        return jsonify({'error': 'Failed to fetch city coordinates'}), geocoding_response.status_code

    city_data = geocoding_response.json()
    lat = city_data['coord']['lat']
    lon = city_data['coord']['lon']

    forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={query}&appid={openweather_api_key}&units=metric'
    forecast_response = requests.get(forecast_url)

    if forecast_response.status_code != 200:
        return jsonify({'error': 'Error fetching weather data'}), forecast_response.status_code

    forecast_data = forecast_response.json()

    return jsonify(forecast_data)