import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Blueprint, jsonify, request
from app import db
from app.models.expense import Expense
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime


expense = Blueprint('expense', __name__, url_prefix="/expenses")


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
        
        # return jsonify({"message": "Expense added successfully"}), 201
        return jsonify(new_expense.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500


@expense.route('', methods=['GET'])
@jwt_required()
def get_expenses():
    current_user = get_jwt_identity().get('id')
    expenses = Expense.query.filter_by(user_id=current_user).order_by(Expense.date.desc()).all()
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
    # return jsonify(expense.to_dict()), 201


