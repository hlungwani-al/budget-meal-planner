from flask import Blueprint, jsonify, request
from services.meal_service import MealService

meal_routes = Blueprint('meal_routes', __name__)

@meal_routes.route('/api/suggest', methods=['POST'])
def suggest_groceries():
    data = request.get_json()
    if not data or 'budget' not in data:
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

    budget = float(data['budget'])
    meal_type = data.get('meal_type', 'high-protein')

    if budget <= 0:
        return jsonify({'success': False, 'error': 'Budget must be positive'}), 400

    result = MealService.suggest_groceries(budget, meal_type)
    return jsonify({
        'success': True,
        **result
    })
