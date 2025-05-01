from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.school import School
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import uuid

bp = Blueprint('user', __name__, url_prefix='/api/users')

@bp.route('/schools/<school_id>/users', methods=['POST'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print("Registration data received:", data)  # Debug print
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        # Extract data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role', 'owner')  # Default to owner for first user
        school_name = data.get('school_name')
        
        print(f"Email: {email}, Name: {first_name} {last_name}, Role: {role}")  # Debug print
        
        # Validate data
        if not all([email, password, first_name, last_name]):
            return jsonify({'message': 'Missing required fields'}), 400

        if role not in ['owner', 'educator', 'student']:
            return jsonify({'message': 'Invalid role'}), 400

        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists'}), 400

        # Create a new school
        if school_name:
            print(f"Creating new school: {school_name}")  # Debug print
            school = School(name=school_name)
            db.session.add(school)
            db.session.flush()  # Get the ID without committing
            school_id = school.id
            print(f"New school created with ID: {school_id}")  # Debug print
        else:
            # Try to find an existing school
            print("Looking for existing schools")  # Debug print
            existing_school = School.query.first()
            if existing_school:
                school_id = existing_school.id
                print(f"Using existing school with ID: {school_id}")  # Debug print
            else:
                print("No school found and no school_name provided")  # Debug print
                return jsonify({'message': 'School name is required for first registration'}), 400

        # Create new user with properly hashed password
        print(f"Creating user with school_id: {school_id}")  # Debug print
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            first_name=first_name,
            last_name=last_name,
            school_id=school_id
        )
        
        db.session.add(user)
        db.session.commit()
        print(f"User created with ID: {user.id}")  # Debug print
        
        # Generate token for immediate login
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'User registered successfully',
            'user_id': str(user.id),
            'token': access_token,
            'school_id': str(school_id)
        }), 201
            
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'An error occurred during registration', 'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
            
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        if not check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Invalid password'}), 401
            
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'token': access_token,
            'user_id': str(user.id),
            'role': user.role,
            'school_id': str(user.school_id)
        }), 200
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'An error occurred during login', 'error': str(e)}), 500