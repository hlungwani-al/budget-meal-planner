import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connections

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

class GroceryItem(db.Model):
    __tablename__ = 'grocery_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'protein', 'vegetarian', etc.
    price = db.Column(db.Float, nullable=False)
    store = db.Column(db.String(50), nullable=False)
    protein_per_100g = db.Column(db.Float)
    last_updated = db.Column(db.Date, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class MealPlan(db.Model):
    __tablename__ = 'meal_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    budget = db.Column(db.Float, nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# API Routes
@app.route('/api/suggest', methods=['POST'])
def suggest_groceries():
    """Generate grocery suggestions based on budget and meal type"""
    try:
        data = request.get_json()

        if not data or 'budget' not in data:
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

        budget = float(data['budget'])
        meal_type = data.get('meal_type', 'high-protein')

        if budget <= 0:
            return jsonify({'success': False, 'error': 'Budget must be positive'}), 400

        # Get matching items sorted by best protein-to-price ratio
        items = GroceryItem.query.filter(
            GroceryItem.category.ilike(f'%{meal_type}%')
        ).order_by(
            (GroceryItem.protein_per_100g/GroceryItem.price).desc()
        ).all()

        if not items:
            return jsonify({'success': False, 'error': 'No items found for the given meal type'}), 404

        suggestions = []
        remaining = budget

        # Try to get a variety of items rather than just the cheapest
        for item in items:
            if item.price <= remaining:
                # Check if we already have an item from this store to diversify
                if not any(i['store'] == item.store for i in suggestions):
                    suggestions.append({
                        'id': item.id,
                        'name': item.name,
                        'price': item.price,
                        'store': item.store,
                        'protein': item.protein_per_100g,
                        'value': round(item.protein_per_100g/item.price, 2)
                    })
                    remaining -= item.price

        if not suggestions:
            return jsonify({'success': False, 'error': 'No items could be purchased with the given budget'}), 400

        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'stats': {
                'total_spent': round(budget - remaining, 2),
                'remaining_budget': round(remaining, 2),
                'protein_per_rand': round(
                    sum(i['protein'] for i in suggestions) / (budget - remaining), 2
                ) if (budget - remaining) > 0 else 0,
                'total_protein': round(sum(i['protein'] for i in suggestions), 2)
            }
        })

    except ValueError as ve:
        return jsonify({'success': False, 'error': f'Invalid parameter: {str(ve)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/api/items', methods=['GET'])
def list_items():
    """List all grocery items in the database with additional details"""
    items = GroceryItem.query.all()
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
            'value_for_money': round(item.protein_per_100g / item.price, 2) if item.price > 0 else 0,
            'user_id': item.user_id
        } for item in items]
    })

@app.route('/api/items', methods=['POST'])
def add_item():
    """Add a new grocery item to the database"""
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'category' not in data or 'price' not in data or 'store' not in data or 'protein_per_100g' not in data or 'user_id' not in data:
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

        new_item = GroceryItem(
            name=data['name'],
            category=data['category'],
            price=data['price'],
            store=data['store'],
            protein_per_100g=data['protein_per_100g'],
            user_id=data['user_id']
        )

        db.session.add(new_item)
        db.session.commit()

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
                'value_for_money': round(new_item.protein_per_100g / new_item.price, 2) if new_item.price > 0 else 0,
                'user_id': new_item.user_id
            }
        })

    except ValueError as ve:
        return jsonify({'success': False, 'error': f'Invalid parameter: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/api/items/<int:item_id>', methods=['PATCH'])
def update_item(item_id):
    """Update an existing grocery item in the database"""
    try:
        data = request.get_json()
        item = GroceryItem.query.get(item_id)

        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        if 'name' in data:
            item.name = data['name']
        if 'category' in data:
            item.category = data['category']
        if 'price' in data:
            item.price = data['price']
        if 'store' in data:
            item.store = data['store']
        if 'protein_per_100g' in data:
            item.protein_per_100g = data['protein_per_100g']
        if 'user_id' in data:
            item.user_id = data['user_id']

        db.session.commit()

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
                'value_for_money': round(item.protein_per_100g / item.price, 2) if item.price > 0 else 0,
                'user_id': item.user_id
            }
        })

    except ValueError as ve:
        return jsonify({'success': False, 'error': f'Invalid parameter: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an existing grocery item from the database"""
    try:
        item = GroceryItem.query.get(item_id)

        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        db.session.delete(item)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Item deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database without sample data"""
    db.create_all()
    print("Database initialized")

if __name__ == '__main__':
    app.run(debug=True)
