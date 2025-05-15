import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

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
        budget = float(data['budget'])
        meal_type = data.get('meal_type', 'high-protein')
        
        # Get matching items sorted by best protein-to-price ratio
        items = GroceryItem.query.filter(
            GroceryItem.category.ilike(f'%{meal_type}%')
        ).order_by(
            (GroceryItem.protein_per_100g/GroceryItem.price).desc()
        ).all()
        
        suggestions = []
        remaining = budget
        
        for item in items:
            if item.price <= remaining:
                suggestions.append({
                    'id': item.id,
                    'name': item.name,
                    'price': item.price,
                    'store': item.store,
                    'protein': item.protein_per_100g,
                    'value': round(item.protein_per_100g/item.price, 2)
                })
                remaining -= item.price
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'stats': {
                'total_spent': round(budget - remaining, 2),
                'remaining_budget': round(remaining, 2),
                'protein_per_dollar': round(
                    sum(i['protein'] for i in suggestions) / (budget - remaining), 2
                ) if (budget - remaining) > 0 else 0
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database with sample data"""
    db.create_all()
    
    if not GroceryItem.query.first():
        sample_items = [
            GroceryItem(
                name='Chicken Breast',
                price=5.99,
                store='Walmart',
                category='high-protein',
                protein_per_100g=31.0
            ),
            GroceryItem(
                name='Eggs (Dozen)',
                price=3.49,
                store='Costco',
                category='high-protein',
                protein_per_100g=13.0
            ),
            GroceryItem(
                name='Greek Yogurt',
                price=2.99,
                store='Whole Foods',
                category='high-protein',
                protein_per_100g=10.0
            )
        ]
        db.session.bulk_save_objects(sample_items)
        db.session.commit()
        print("Database initialized with sample data")

if __name__ == '__main__':
    app.run(debug=True)