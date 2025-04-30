from flask import Blueprint, request, jsonify
from .. import db
from ..models.school import School
from ..utils.auth import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User

bp = Blueprint('schools', __name__)

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