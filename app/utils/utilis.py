from app.models.user import User

def is_educator(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'educator'