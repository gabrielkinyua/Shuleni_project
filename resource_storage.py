from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/shuleni'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'we will add'  
app.config['UPLOAD_FOLDER'] = 'uploads'  
jwt = JWTManager(app)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class School(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('school.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # owner/manager, educator, student

class Class(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('school.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Resource(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('school.id'), nullable=False)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)

class ResourcePermission(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    resource_id = db.Column(db.String(36), db.ForeignKey('resource.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('class.id'), nullable=False)

# check if user is educator
def is_educator(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'educator'

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

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

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

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

# minitests for rescources.py
import unittest
from app import app, db
from flask_jwt_extended import create_access_token
import os
import uuid
from io import BytesIO

class ResourceTests(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/shuleni_test'
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        self.client = app.test_client()
        db.create_all()

        # Create test school, educator, and class
        self.school = School(id=str(uuid.uuid4()), name='Test School')
        self.educator = User(id=str(uuid.uuid4()), school_id=self.school.id, email='educator@test.com', role='educator')
        self.student = User(id=str(uuid.uuid4()), school_id=self.school.id, email='student@test.com', role='student')
        self.class_ = Class(id=str(uuid.uuid4()), school_id=self.school.id, name='Class A')
        db.session.add_all([self.school, self.educator, self.student, self.class_])
        db.session.commit()

        self.educator_token = create_access_token(identity=self.educator.id)
        self.student_token = create_access_token(identity=self.student.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
        os.rmdir(app.config['UPLOAD_FOLDER'])

    def test_upload_resource(self):
        response = self.client.post(
            f'/schools/{self.school.id}/resources',
            data={'file': (BytesIO(b'Test content'), 'test.txt')},
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['filename'], 'test.txt')

    def test_get_resources_educator(self):
        resource = Resource(
            id=str(uuid.uuid4()), school_id=self.school.id, uploaded_by=self.educator.id,
            filename='test.txt', filepath='uploads/test.txt'
        )
        db.session.add(resource)
        db.session.commit()

        response = self.client.get(
            f'/schools/{self.school.id}/resources',
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['filename'], 'test.txt')

    def test_update_permissions(self):
        resource = Resource(
            id=str(uuid.uuid4()), school_id=self.school.id, uploaded_by=self.educator.id,
            filename='test.txt', filepath='uploads/test.txt'
        )
        db.session.add(resource)
        db.session.commit()

        response = self.client.put(
            f'/resources/{resource.id}/permissions',
            json={'class_ids': [self.class_.id]},
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Permissions updated')

if __name__ == '__main__':
    unittest.main()