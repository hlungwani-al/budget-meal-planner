from flask import Blueprint, jsonify, request
from services.grocery_service import GroceryService

grocery_routes = Blueprint('grocery_routes', __name__)

@grocery_routes.route('/api/get_items', methods=['GET'])
def list_items():
    items = GroceryService.get_all_items()
    return jsonify({
        'success': True,
        'count': len(items),
        'items': [{
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'price': item.price,
            'store': item.store,
            'protein_per_100g': item.protein_per_100g,
            'last_updated': item.last_updated.isoformat() if item.last_updated else None,
            'user_id': item.user_id
        } for item in items]
    })

@grocery_routes.route('/api/add_item', methods=['POST'])
def add_item():
    data = request.get_json()
    new_item = GroceryService.add_item(data)
    if not new_item:
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

    return jsonify({
        'success': True,
        'message': 'Item added successfully',
        'item': {
            'id': new_item.id,
            'name': new_item.name,
            'category': new_item.category,
            'price': new_item.price,
            'store': new_item.store,
            'protein_per_100g': new_item.protein_per_100g,
            'last_updated': new_item.last_updated.isoformat() if new_item.last_updated else None,
            'user_id': new_item.user_id
        }
    })

@grocery_routes.route('/api/update_item/<int:item_id>', methods=['PATCH'])
def update_item(item_id):
    data = request.get_json()
    item = GroceryService.update_item(item_id, data)
    if not item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Item updated successfully',
        'item': {
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'price': item.price,
            'store': item.store,
            'protein_per_100g': item.protein_per_100g,
            'last_updated': item.last_updated.isoformat() if item.last_updated else None,
            'user_id': item.user_id
        }
    })

@grocery_routes.route('/api/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    success = GroceryService.delete_item(item_id)
    if not success:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Item deleted successfully'
    })
