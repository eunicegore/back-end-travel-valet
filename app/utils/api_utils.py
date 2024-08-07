from flask import current_app
import requests
import logging


def get_coordinates(location):
    try:
        # Construct the URL for the geocoding api request:
        geo_url = f"{current_app.config['GEOCODING_API_URL']}?q={location}&appid={current_app.config['OPENWEATHER_API_KEY']}"

        # Make the request to the API:
        response = requests.get(geo_url)
        response.raise_for_status()     # raise an HTTP error for bad responses

        data = response.json()
        logging.info(f'Received geocoding data: {data}')

        # Check if response has expected data:
        if not isinstance(data, list) or not data:
            return None, 'No results found'
        
        if 'lat' not in data[0] or 'lon' not in data[0]:    # data is a list of dictionaries the response is the first dict in the list:
            return None, 'Latitude or Longitude not found'
    
        # return data  # Returns all the data from the API

        # Only get coordinates from the response to pass them to the weather API:
        lat = data[0]['lat']
        lon = data[0]['lon']

        logging.info(f'Return response: {(lat,lon)}')
        return(lat,lon), None
    
    except requests.RequestException as e:
        logging.error(f"Geocoding request failed: {e}")
        return None, str(e)