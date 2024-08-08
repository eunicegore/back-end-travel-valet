from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import requests
import logging

# Define flask blueprint:
dining_routes_bp = Blueprint('dining_routes', __name__)


@dining_routes_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def dining_recommendations():
    # Retrieve query parameters from user input:
    city = request.args.get('city')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    term = request.args.get('term')

    # Validate required parameters:
    if not city and (not latitude or not longitude):
        return jsonify({'error': 'City or geo location are required'}), 400

    headers = {'Authorization': f"Bearer {current_app.config['YELP_API_KEY']}"}
    params = {
        'term': term,
        # Restricts results to only get restaurants and bars
        'categories': 'restaurants, bars',
        'sort_by': 'rating',
        'limit': 50    # Yelp's max number of results returned
    }

    # If available add location-based parameters:
    if latitude and longitude:
        params['latitude'] = latitude
        params['longitude'] = longitude
    elif city:
        params['location'] = city

    # Construct the full URL for the Yelp request - ("/businesses/search" -- endpoint from Yelp)
    api_url = f"{current_app.config['YELP_API_URL']}/businesses/search"

    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch data from Yelp API'}), 500

    data = response.json()
    # return jsonify(data) #Returns all available data for the different businesses

    recommendations = []   # creates response: list of dictionaries with a few specific fields

    for business in data.get('businesses', []):
        recommendations.append({
            'id': business.get('id'),
            'name': business.get('name'),
            # 'categories' in the data is an array of dictionaries, each dictionary has a key: 'title'
            'categories': [category['title'] for category in business.get('categories', [])],
            # in the data display_address is an aray of strings and it's part of a dictionary named 'location'
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
    return jsonify({'recommendations': recommendations})
