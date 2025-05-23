import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from models.user import db
from routes.grocery_routes import grocery_routes
from routes.meal_routes import meal_routes
from routes.user_routes import user_routes

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connections

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(grocery_routes)
app.register_blueprint(meal_routes)
app.register_blueprint(user_routes)

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database without sample data"""
    db.create_all()
    print("Database initialized")

if __name__ == '__main__':
    app.run(debug=True)
