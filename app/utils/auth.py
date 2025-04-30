from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from functools import wraps
from flask import jsonify

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get_or_404(user_id)
            if user.role not in roles:
                return jsonify({'error': 'Unauthorized access'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator