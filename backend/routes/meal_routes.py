from flask import Blueprint, jsonify, request
from services.meal_service import MealService

meal_routes = Blueprint('meal_routes', __name__)

@meal_routes.route('/api/suggest', methods=['POST'])
def suggest_groceries():
    data = request.get_json()
    if not data or 'budget' not in data or 'user_id' not in data:
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

    budget = float(data['budget'])
    meal_type = data.get('meal_type', 'high-protein')
    user_id = data['user_id']

    if budget <= 0:
        return jsonify({'success': False, 'error': 'Budget must be positive'}), 400

    try:
        result = MealService.suggest_groceries(budget, meal_type, user_id)
        return jsonify({
            'success': True,
            **result
        })
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}), 500

@meal_routes.route('/api/meal-plans', methods=['GET'])
def get_all_meal_plans():
    meal_plans = MealService.get_all_meal_plans()
    return jsonify({
        'success': True,
        'count': len(meal_plans),
        'meal_plans': [{
            'id': meal_plan.id,
            'user_id': meal_plan.user_id,
            'budget': meal_plan.budget,
            'meal_type': meal_plan.meal_type,
            'created_at': meal_plan.created_at.isoformat() if meal_plan.created_at else None
        } for meal_plan in meal_plans]
    })
