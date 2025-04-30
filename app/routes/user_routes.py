from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.school import School
from app.utils.auth import role_required
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required

bp = Blueprint('users', __name__)

@bp.route('/schools/<school_id>/users', methods=['POST'])
@role_required('owner')
def add_user(school_id):
    school = School.query.get_or_404(school_id)
    data = request.get_json()
    
    required_fields = ['email', 'password', 'role', 'first_name', 'last_name']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['role'] not in ['owner', 'educator', 'student']:
        return jsonify({'error': 'Invalid role'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        school_id=school_id,
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data['role'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name
    }), 201

@bp.route('/users/<user_id>', methods=['PUT'])
@role_required('owner')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    allowed_fields = ['email', 'role', 'first_name', 'last_name', 'password']
    for key in data:
        if key not in allowed_fields:
            return jsonify({'error': f'Cannot update {key}'}), 400
    
    if 'email' in data and data['email'] != user.email and User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    if 'role' in data and data['role'] not in ['owner', 'educator', 'student']:
        return jsonify({'error': 'Invalid role'}), 400
    
    for key, value in data.items():
        if key == 'password':
            setattr(user, 'password_hash', generate_password_hash(value))
        else:
            setattr(user, key, value)
    
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name
    })

@bp.route('/users/<user_id>', methods=['DELETE'])
@role_required('owner')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(
        school_id="temp", email=data['email'], role='owner',
        password_hash=generate_password_hash(data['password']),
        first_name=data['first_name'], last_name=data['last_name']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        token = create_access_token(identity=user.id)
        return jsonify({'token': token}), 200
    return jsonify({'error': 'User not found'}), 404