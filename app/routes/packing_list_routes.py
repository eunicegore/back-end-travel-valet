import logging
from flask import Blueprint, request, jsonify
from app import db
from app.models.packing_list import PackingList
from flask_jwt_extended import jwt_required, get_jwt_identity

# Defines new flask blueprint:
packing_list_bp = Blueprint('packing_list', __name__, url_prefix='/packing_list')

# Route to Add an Item:
@packing_list_bp.route('', methods=['POST'])
@jwt_required()
def add_item():
    data = request.get_json()
    item_name = data.get('item_name')

    if not item_name:
        return jsonify({'message': 'Item name is required'}), 400
    

    try:
        current_user = get_jwt_identity().get('id')
        logging.debug(f'JWT identity: {current_user}')
        
        new_item = PackingList(item_name=item_name, user_id=current_user)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Item added to packing list'}), 201
    except Exception as e: 
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Route to Get items list:
@packing_list_bp.route('', methods=['GET'])
@jwt_required()
def get_items():
    current_user = get_jwt_identity().get('id')
    items = PackingList.query.filter_by(user_id=current_user).all()
    return jsonify([item.to_dict() for item in items]), 200

    
# Route to Delete an item:
@packing_list_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_item(id):
    current_user = get_jwt_identity().get('id')
    item = PackingList.query.get_or_404(id)

    if item.user_id != current_user:
        return jsonify({'message': 'Unauthorized user'}), 403
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'}), 200


# Route to Update an item:
@packing_list_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_item(id):
    current_user = get_jwt_identity().get('id')
    data = request.get_json()
    item = PackingList.query.get_or_404(id)
    
    if item.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    item.item_name = data.get('item name', item.item_name)
    item.is_packed = data.get('is_packed', item.is_packed)
    db.session.commit()
    return jsonify({'message': 'Item updated'}), 200
