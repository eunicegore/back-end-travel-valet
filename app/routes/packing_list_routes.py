from app import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.packing_list import PackingList
from app.models.item import Item

# Defines new flask blueprint:
packing_list_bp = Blueprint('packing_list', __name__, url_prefix='/packing-list')

# Route to Create a New List:
@packing_list_bp.route('', methods=['POST'])
@jwt_required()
def create_list():
    data = request.get_json()
    list_name = data.get('listName')
    items_data = data.get('items', [])

    if not list_name:
        return jsonify({'message': 'List name is required'}), 400
    
    try:
        current_user = get_jwt_identity().get('id')
        new_list = PackingList(listName=list_name, user_id=current_user)
        
        db.session.add(new_list)
        db.session.flush()  # Use flush to get the id for the new list

        # Create PackingListItem objects
        items = [
            Item(
                description=item['description'],
                quantity=item.get('quantity', 1),
                packed=item.get('packed', False),
                listId=new_list.id
            ) 
            for item in items_data
        ]
        db.session.add_all(items)
        db.session.commit()

        response_data = new_list.to_dict()

        return jsonify({'message': 'New packing list created', 'packingList': response_data}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Route to Get all Lists:
@packing_list_bp.route('', methods=['GET'])
@jwt_required()
def get_lists():
    current_user = get_jwt_identity().get('id')
    lists = PackingList.query.filter_by(user_id=current_user).all()

    if not lists:
        return jsonify([]), 200
    
    response_data = [packing_list.to_dict() for packing_list in lists]
    
    return jsonify(response_data), 200


# Route to Delete a list:
@packing_list_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_list(id):
    current_user = get_jwt_identity().get('id')
    packing_list = PackingList.query.filter_by(id=id, user_id=current_user).first()

    if packing_list is None:
        return jsonify({'message': 'Packing list not found or user not authorized user'}), 404
    
    try:
        db.session.delete(packing_list)
        db.session.commit()
        return jsonify({'message': 'Packing list deleted!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Route to Update the items in a list:
@packing_list_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_list(id):
    current_user = get_jwt_identity().get('id')
    data = request.get_json()
    packing_list = PackingList.query.filter_by(id=id, user_id=current_user).first_or_404()

    list_name = data.get('listName')
    items_data = data.get('items', [])

    # Update list name if provided:
    if list_name is not None:
        packing_list.listName = list_name

    try:
        # Add new items from the request:
        for item_data in items_data:
            item_id = item_data.get('id')
            description = item_data.get('description')
            quantity = item_data.get('quantity')
            packed = item_data.get('packed')

            if item_id is None:
                # Add new item:
                new_item = Item(
                    description=description,
                    quantity=quantity,
                    packed=packed,
                    listId=packing_list.id
                )
                db.session.add(new_item)
        
        db.session.commit()
        updated_packing_list = PackingList.query.get(id)
        return jsonify({'message': 'Packing list updated', 'packing_list': updated_packing_list.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating itme'}), 500


# Route to Get a packing list by ID:
@packing_list_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_list_by_id(id):
    current_user = get_jwt_identity().get('id')
    packing_list = PackingList.query.filter_by(id=id, user_id=current_user).first()
    
    if packing_list is None:
        return jsonify({'message': 'Packing list not found'}), 404
    
    return jsonify(packing_list.to_dict()), 200
        
