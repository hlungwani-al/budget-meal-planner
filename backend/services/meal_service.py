from models.meal_plan import MealPlan
from models.grocery_item import GroceryItem
from models.user import db

class MealService:
    @staticmethod
    def suggest_groceries(budget, meal_type):
        items = GroceryItem.query.filter(
            GroceryItem.category.ilike(f'%{meal_type}%')
        ).order_by(
            (GroceryItem.protein_per_100g/GroceryItem.price).desc()
        ).all()

        suggestions = []
        remaining = budget

        for item in items:
            if item.price <= remaining:
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

        return {
            'suggestions': suggestions,
            'stats': {
                'total_spent': round(budget - remaining, 2),
                'remaining_budget': round(remaining, 2),
                'protein_per_rand': round(
                    sum(i['protein'] for i in suggestions) / (budget - remaining), 2
                ) if (budget - remaining) > 0 else 0,
                'total_protein': round(sum(i['protein'] for i in suggestions), 2)
            }
        }
