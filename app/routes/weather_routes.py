from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.utils.api_utils import get_coordinates
import requests
import logging

weather_routes_bp = Blueprint('weather_routes', __name__)

@weather_routes_bp.route('/weather', methods=['GET'])
@jwt_required()
def get_weather():

    # Get params from the request:
    location = request.args.get('location')

    if not location:
        return jsonify({'error': 'Location is required'}), 400
    
    # Call utility function get_coordinates to get the latitude and longitude:
    coordinates, error = get_coordinates(location)

    if error:
        return jsonify({'error': error}), 500
    
    if coordinates is None:
        return jsonify({'error': 'Unable to fetch coordinates'}), 500
    
    lat, lon = coordinates


    try:
        # URL for the weather API request:
        api_url = f"{current_app.config['WEATHER_API_URL']}?lat={lat}&lon={lon}&appid={current_app.config['OPENWEATHER_API_KEY']}"
        
        # Make request to the API:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()

        logging.info(f'Received data: {data}')

        return jsonify(data)
    
    except requests.RequestException as e:
        logging.error(f'Weather API request failed: {e}')
        return jsonify({'error': str(e)}, 500)

