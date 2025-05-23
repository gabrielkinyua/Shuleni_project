from flask import Blueprint, request, jsonify
from app import db
from app.models.school import School
from app.utils.auth import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.assessment import Class

bp = Blueprint('school', __name__, url_prefix='/api/schools')

@bp.route('/schools', methods=['POST'])
@jwt_required()
def create_school():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role != 'owner':
        return jsonify({'error': 'Only school owners can create schools'}), 403
    
    if not data or not data.get('name'):
        return jsonify({'error': 'School name is required'}), 400
    
    school = School(name=data['name'])
    db.session.add(school)
    db.session.commit()
    
    return jsonify({
        'id': school.id,
        'name': school.name,
        'created_at': school.created_at.isoformat()
    }), 201

@bp.route('/schools/<school_id>/classes', methods=['POST'])
@jwt_required()
@role_required('owner')
def create_class(school_id):
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Class name is required'}), 400
    class_ = Class(school_id=school_id, name=data['name'])
    db.session.add(class_)
    db.session.commit()
    return jsonify({'id': class_.id}), 201