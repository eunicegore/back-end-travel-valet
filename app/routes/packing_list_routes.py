from app import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.packing_list import PackingList
from app.models.packing_list_item import PackingListItem

# Defines new flask blueprint:
packing_list_bp = Blueprint('packing_list', __name__, url_prefix='/packing-list')

# Route to Create a New List:
@packing_list_bp.route('', methods=['POST'])
@jwt_required()
def create_list():
    data = request.get_json()
    list_name = data.get('list_name')
    items_data = data.get('items', [])

    if not list_name:
        return jsonify({'message': 'List name is required'}), 400
    
    try:
        current_user = get_jwt_identity().get('id')
        new_list = PackingList(list_name=list_name, user_id=current_user)
        db.session.add(new_list)
        db.session.flush()  # Use flush to get the id for the new list

        # Create PackingListItem objects
        items = [
            PackingListItem(
                item_name=item['item_name'],
                quantity=item.get('quantity', 1),
                packed_quantity=item.get('packed_quantity', 0),
                is_packed=item.get('is_packed', False),
                packing_list_id=new_list.id
            ) for item in items_data
        ]
        db.session.add_all(items)
        db.session.commit()

        return jsonify({'message': 'New packing list created', 'packing_list': new_list.to_dict()}), 201
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
        return jsonify({'message': 'No packing lists found'}), 404

    return jsonify([packing_list.to_dict() for packing_list in lists]), 200


# Route to Delete a list:
@packing_list_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_list(id):
    current_user = get_jwt_identity().get('id')
    packing_list = PackingList.query.get_or_404(id)

    if packing_list.user_id != current_user:
        return jsonify({'message': 'Unauthorized user'}), 403
    
    db.session.delete(packing_list)
    db.session.commit()
    return jsonify({'message': 'Packing list deleted'}), 200


# Route to Update the items in a list:
@packing_list_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_list(id):
    current_user = get_jwt_identity().get('id')
    data = request.get_json()
    packing_list = PackingList.query.get_or_404(id)

    if packing_list.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    list_name = data.get('list_name')
    items_data = data.get('items', [])

    if list_name is not None:
        packing_list.list_name = list_name

    try:
        # Get current items that are in the packing list:
        current_items = PackingListItem.query.filter_by(packing_list_id=packing_list.id).all()
        current_items_dict = {item.id: item for item in current_items}

        updated_item_ids = set()

        # Update items or add a new ones from the request:
        for item_data in items_data:
            item_id = item_data.get('item_id')
            item_name = item_data.get('item_name')
            quantity = item_data.get('quantity')
            packed_quantity = item_data.get('packed_quantity')
            is_packed = item_data.get('is_packed')

            if item_id and item_id in current_items_dict:
                # Update existing item:
                item = current_items_dict[item_id]
                if item_name is not None:
                    item.item_name = item_name
                if quantity is not None:
                    item.quantity = quantity
                if item.packed_quantity is not None:
                    item.packed_quantity = packed_quantity
                if is_packed is not None:
                    item.is_packed = is_packed
                updated_item_ids.add(item_id)
            elif item_id is None:
                # Create and add new item:
                new_item = PackingListItem(
                    item_name=item_name,
                    quantity=quantity,
                    packed_quantity=packed_quantity,
                    is_packed=is_packed,
                    packing_list_id=packing_list.id
                )
                db.session.add(new_item)
        
        db.session.commit()

        # Check that the response shows the current state of the list:
        updated_packing_list = PackingList.query.get(id)
        return jsonify({'message': 'Packing list updated', 'packing_list': updated_packing_list.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating packing list'}), 500


# Route to Get a packing list by ID:
@packing_list_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_list_by_id(id):
    current_user = get_jwt_identity().get('id')
    packing_list = PackingList.query.get(id)

    if packing_list is None:
        return jsonify({'message': 'Packing list not found'}), 404

    if packing_list.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    return jsonify(packing_list.to_dict()), 200
        

# Route to delete an item from a packing list:
@packing_list_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    current_user = get_jwt_identity().get('id')
    item = PackingListItem.query.get_or_404(item_id)

    # Check if the item belongs to the current user:
    if item.packing_list.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try: 
        db.session.delete(item)
        db.session.commit()

        # get the updated list without the removed item:
        updated_packing_list = PackingList.query.get(item.packing_list_id)

        return jsonify({'message': 'Item deleted', 'packing_list': updated_packing_list.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting item', 'error': str(e)}), 500
    