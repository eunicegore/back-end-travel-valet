from app import db
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.packing_list import PackingList
from app.models.packing_list_item import PackingListItem

# Defines new flask blueprint:
packing_list_item_bp = Blueprint('packing_list_item', __name__, url_prefix='/packing-list')

# Route to Add new item to packing list:
@packing_list_item_bp.route('/<int:id>/items', methods=['POST'])
@jwt_required()
def add_item_to_list(id):
    current_user = get_jwt_identity().get('id')
    data = request.get_json()
    item_name = data.get('item_name')
    quantity = data.get('quantity', 1)
    packed_quantity = data.get('packed_quantity', 0)
    is_packed = data.get('is_packed', False)

    if not item_name: 
        return jsonify({'message': 'Item name is required'}), 400
    
    packing_list = PackingList.query.get_or_404(id)
    if packing_list.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        new_item = PackingListItem(
            item_name=item_name,
            quantity=quantity,
            packed_quantity=packed_quantity,
            is_packed=is_packed,
            packing_list_id=packing_list.id
        )
        db.session.add(new_item)
        db.session.commit()

        return jsonify({'message': 'Item added to list', 'item': new_item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Route to Delete a specific item:
@packing_list_item_bp.route('/items/<int:item_id>', methods=['DELETE'])
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


# Route to Toggle the item's Packed status:
@packing_list_item_bp.route('/items/<int:item_id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_packed_status(item_id):
    current_user = get_jwt_identity().get('id')
    item = PackingListItem.query.get(item_id)

    if not item:
        return jsonify({'message': 'Item not found'}), 404

    if item.packing_list.user_id != current_user:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        item.is_packed = not item.is_packed
        db.session.commit()
        return jsonify({'message': 'Item status toggled', 'item': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500