from flask import Blueprint, jsonify, request
from services.user_service import UserService

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data or 'password_hash' not in data:
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

    new_user = UserService.add_user(data)
    return jsonify({
        'success': True,
        'message': 'User added successfully',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }
    })

@user_routes.route('/api/users', methods=['GET'])
def get_all_users():
    users = UserService.get_all_users()
    return jsonify({
        'success': True,
        'count': len(users),
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email
        } for user in users]
    })

@user_routes.route('/api/users', methods=['DELETE'])
def delete_all_users():
    success = UserService.delete_all_users()
    if not success:
        return jsonify({'success': False, 'error': 'Failed to delete users'}), 500

    return jsonify({
        'success': True,
        'message': 'All users deleted successfully'
    })

@user_routes.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    success = UserService.delete_user(user_id)
    if not success:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'User deleted successfully'
    })
