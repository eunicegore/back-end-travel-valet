import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Blueprint, jsonify, request
from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token, jwt_required


auth=Blueprint('auth', __name__,url_prefix="/user")

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    logging.debug(f'Received registration data: {data}')
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if not username or not password or not email:
        logging.error('Missing required fields')
        return jsonify({'message': 'Username, password, email are required'}), 400
    if User.query.filter_by(username=username).first():
        logging.error(f'User {username} already exists')
        return jsonify({'message': 'User already exists'}), 400
    new_user=User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    logging.debug(f'User {username} registered successfully')
    return jsonify({'message': 'User registered!'})

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity={'id':user.id})
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Invalid credentials"}), 401
