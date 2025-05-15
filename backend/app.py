from flask import Flask
from src.utils.database import db
from src.routes import meal_plans, groceries, auth

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(meal_plans.meal_plans_bp, url_prefix='/api')
    app.register_blueprint(groceries.groceries_bp, url_prefix='/api')
    app.register_blueprint(auth.auth_bp, url_prefix='/api/auth')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)