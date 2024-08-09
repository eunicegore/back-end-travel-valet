from app import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.packing_list import PackingList
from app.models.item import Item

# Defines new flask blueprint:
item_bp = Blueprint('item', __name__, url_prefix='/packing-list/<int:listId>/items')

# Route to Add new item to packing list:
@item_bp.route('', methods=['POST'])
@jwt_required()
def add_item_to_list(listId):
    current_user = get_jwt_identity().get('id')
    data = request.get_json()

    description = data.get('description')
    quantity = data.get('quantity', 1)
    packed = data.get('packed', False)

    if not description: 
        return jsonify({'message': 'Item descrition is required'}), 400
    
    packing_list = PackingList.query.filter_by(id=listId, user_id=current_user).first_or_404()
    
    try:
        new_item = Item(
            description=description,
            quantity=quantity,
            packed=packed,
            listId=packing_list.id
        )
        db.session.add(new_item)
        db.session.commit()

        return jsonify({'message': 'Item added to list', 'item': new_item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Route to Delete a specific item:
@item_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_item(listId, id):
    current_user = get_jwt_identity().get('id')
    item = Item.query.filter_by(id=id, listId=listId).first_or_404()

    # Check if the item belongs to the current user:
    if item.packing_list.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try: 
        db.session.delete(item)
        db.session.commit()

        # get the updated list without the removed item:
        updated_packing_list = PackingList.query.get(listId)

        return jsonify({'message': 'Item deleted', 'packing_list': updated_packing_list.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting item', 'error': str(e)}), 500


# Route to Toggle the item's Packed status:
@item_bp.route('/<int:id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_packed_status(listId, id):
    current_user = get_jwt_identity().get('id')
    item = Item.query.filter_by(id=id, listId=listId).first_or_404()

    if item.packing_list.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        item.packed = not item.packed
        db.session.commit()
        return jsonify({'message': 'Item status toggled', 'item': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500