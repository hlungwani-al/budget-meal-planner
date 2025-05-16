from models.grocery_item import GroceryItem
from models.user import db

class GroceryService:
    @staticmethod
    def get_all_items():
        return GroceryItem.query.all()

    @staticmethod
    def add_item(data):
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
        return new_item

    @staticmethod
    def update_item(item_id, data):
        item = GroceryItem.query.get(item_id)
        if not item:
            return None

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
        return item

    @staticmethod
    def delete_item(item_id):
        item = GroceryItem.query.get(item_id)
        if not item:
            return False

        db.session.delete(item)
        db.session.commit()
        return True
