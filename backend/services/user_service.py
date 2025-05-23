from models.user import User, db

class UserService:
    @staticmethod
    def add_user(data):
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash']
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def delete_all_users():
        User.query.delete()
        db.session.commit()
        return True

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True
