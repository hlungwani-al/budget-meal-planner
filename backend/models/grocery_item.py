from flask_sqlalchemy import SQLAlchemy
from models.user import db

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
