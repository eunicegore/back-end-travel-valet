import logging
logging.basicConfig(level=logging.DEBUG)
import bcrypt
from flask import Blueprint, jsonify, make_response, request, abort
from app import db
from app.models.expense import Expense
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime



auth=Blueprint('auth', __name__,url_prefix="/user")
expense = Blueprint('expense', __name__, url_prefix="/expenses")

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



# @auth.route('/logout', methods=['POST'])
# @jwt_required()
# def logout():
#     return jsonify({'message': 'Logged out!'})

# @login_required
# def logout():
#     logout_user()
#     return jsonify({'message': 'Logged out successfully!'})

@expense.route("", methods=['POST'])
@jwt_required()
def add_expense():
    data = request.get_json()
    amount = data.get('amount')
    description = data.get('description')
    date = data.get('date')
    category = data.get('category')
    
    if not amount or not description or not date or not category:
        return jsonify({"message": "All fields are required"}), 400
    
    
    try:
        current_user = get_jwt_identity().get('id')
        logging.debug(f'JWT identity: {current_user}')
        
    
        new_expense = Expense(
            amount=amount,
            description=description,
            date=datetime.strptime(date, '%Y-%m-%d'),
            user_id=current_user,
            category=category
        )
        db.session.add(new_expense)
        db.session.commit()
        
        return jsonify({"message": "Expense added successfully"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


@expense.route('', methods=['GET'])
@jwt_required()
def get_expenses():
    current_user = get_jwt_identity().get('id')
    expenses = Expense.query.filter_by(user_id=current_user).all()
    return jsonify([{
        'id': expense.id,
        'amount': expense.amount,
        'description': expense.description,
        'category': expense.category,
        'date': expense.date
    } for expense in expenses])

@expense.route('/<id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    current_user = get_jwt_identity().get('id')
    expense = Expense.query.get_or_404(id)
    if expense.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted!'})


@expense.route('/<id>', methods=['PUT'])
@jwt_required()
def update_expense(id):
    current_user = get_jwt_identity().get('id')
    data = request.json
    expense = Expense.query.get_or_404(id)
    if expense.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    expense.amount = data['amount']
    expense.description = data['description']
    expense.category = data['category']
    expense.date = data['date']
    db.session.commit()
    return jsonify({'message': 'Expense updated!'})


