from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
import uuid
from models import db, Resource, ResourcePermission, School, Class, User
from utils import is_educator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/shuleni')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'we will add')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
jwt = JWTManager(app)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db.init_app(app)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# error handler
@app.errorhandler(Exception)
def handle_exception(e):
    db.session.rollback()
    return jsonify({'error': str(e)}), 500

# API Endpoints
@app.route('/schools/<school_id>/resources', methods=['POST'])
@jwt_required()
def upload_resource(school_id):
    user_id = get_jwt_identity()
    if not is_educator(user_id):
        return jsonify({'error': 'Only educators can upload'}), 403

    school = School.query.get(school_id)
    if not school:
        return jsonify({'error': 'School not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    resource = Resource(school_id=school_id, uploaded_by=user_id, filename=file.filename, filepath=filepath)
    db.session.add(resource)
    db.session.commit()

    return jsonify({'id': resource.id, 'filename': resource.filename}), 201

@app.route('/schools/<school_id>/resources', methods=['GET'])
@jwt_required()
def get_resources(school_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.school_id != school_id:
        return jsonify({'error': 'Unauthorized'}), 403

    school = School.query.get(school_id)
    if not school:
        return jsonify({'error': 'School not found'}), 404

    if user.role == 'educator':
        resources = Resource.query.filter_by(school_id=school_id).all()
    else:  # student
        resources = db.session.query(Resource).join(ResourcePermission).filter(
            ResourcePermission.class_id.in_(
                [c.id for c in Class.query.filter_by(school_id=school_id).all()]
            ),
            Resource.school_id == school_id
        ).all()

    return jsonify([{'id': r.id, 'filename': r.filename} for r in resources]), 200

@app.route('/resources/<resource_id>/permissions', methods=['PUT'])
@jwt_required()
def update_permissions(resource_id):
    user_id = get_jwt_identity()
    if not is_educator(user_id):
        return jsonify({'error': 'Only educators can set permissions'}), 403

    resource = Resource.query.get(resource_id)
    if not resource or resource.uploaded_by != user_id:
        return jsonify({'error': 'Resource not found or unauthorized'}), 404

    data = request.get_json()
    if not data or 'class_ids' not in data:
        return jsonify({'error': 'class_ids required'}), 400

    class_ids = data.get('class_ids', [])

    # Clear existing permissions
    ResourcePermission.query.filter_by(resource_id=resource_id).delete()

    # Add new permissions
    for class_id in class_ids:
        if Class.query.filter_by(id=class_id, school_id=resource.school_id).first():
            permission = ResourcePermission(resource_id=resource_id, class_id=class_id)
            db.session.add(permission)

    db.session.commit()
    return jsonify({'message': 'Permissions updated'}), 200

@app.route('/resources/<resource_id>/download', methods=['GET'])
@jwt_required()
def download_resource(resource_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    resource = Resource.query.get(resource_id)
    if not resource or resource.school_id != user.school_id:
        return jsonify({'error': 'Resource not found or unauthorized'}), 404

    # Check permissions for students
    if user.role != 'educator':
        permitted = ResourcePermission.query.filter_by(resource_id=resource_id).filter(
            ResourcePermission.class_id.in_(
                [c.id for c in Class.query.filter_by(school_id=user.school_id).all()]
            )
        ).first()
        if not permitted:
            return jsonify({'error': 'No access to this resource'}), 403

    return send_file(resource.filepath, as_attachment=True, download_name=resource.filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)