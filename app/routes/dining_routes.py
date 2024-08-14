from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import requests
import logging

# Define flask blueprint:
dining_routes_bp = Blueprint('dining_routes', __name__)

@dining_routes_bp.route('/recommendations', methods=['GET'])
# @jwt_required()     # Requires a valid JWT token to access this route
def dining_recommendations():
    # Retrieve query parameters from user input:
    location = request.args.get('city')
    term = request.args.get('term')

    # Validate required parameters:
    if not location:
        return jsonify({'error': 'City or location are required'}), 400
    
    # Set up headers for Yelp API requests, including API key from app config
    headers = {'Authorization': f"Bearer {current_app.config['YELP_API_KEY']}"}
    
    # Set up parameters for Yelp API request
    params = {
        'location': location,
        'term': term,
        'categories': 'restaurants, bars',
        'sort_by': 'rating',
        'limit': 50    # Yelp's max number of results returned
    }

    # Construct the full URL for the Yelp request - ("/businesses/search" -- endpoint from Yelp)
    api_url = f"{current_app.config['YELP_API_URL']}/businesses/search"

    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code != 200:
        logging.error(f"Yelp API request failed with status code {response.status_code}")
        return jsonify({'error': 'Failed to fetch data from Yelp API'}), 500

    data = response.json()
    # return jsonify(data) # Returns all available data for the different businesses
    recommendations = []   # List of dictionaries with a few selected fields

    for business in data.get('businesses', []):
        recommendations.append({
            'id': business.get('id'),
            'name': business.get('name'),
            # In the data is an array of dictionaries, each dictionary has a key: 'title'
            'categories': [category['title'] for category in business.get('categories', [])],
            # In the data display_address is an array of strings and it's part of a dictionary named 'location'
            'address': ' '.join(business.get('location', {}).get('display_address', [])),
            'website': business.get('url'),
            'phone': business.get('display_phone'),
            'rating': business.get('rating'),
            'review_count': business.get('review_count'),
            'image_url': business.get('image_url')
        })

    # Additional local filtering:
    # Exclude specific categories:
    excluded_categories = {'Fast Food', 'Food Trucks', 'Deli', 'Food Stands'}
    recommendations = [rec for rec in recommendations if not any(
        category in excluded_categories for category in rec['categories'])]

    # filter out bussinesses with rating less than 4.0
    recommendations = [rec for rec in recommendations if rec['rating'] >= 4.0]

    # sort by review count - descending:
    recommendations = sorted(
        recommendations, key=lambda x: x['review_count'], reverse=True)

    # Only return top 5 recommendations:
    return jsonify({'recommendations': recommendations[:5]})
