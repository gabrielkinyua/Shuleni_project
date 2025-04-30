import unittest
from app import app, db
from flask_jwt_extended import create_access_token
import os
import uuid
from io import BytesIO
from app.models.school import School
from app.models.user import User
from app.models.source import Resource
from app.models.assessment import Class, ResourcePermission

class ResourceTests(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/shuleni_test'
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

        # Create test school, educator, and class
        self.school = School(id=str(uuid.uuid4()), name='Test School')
        self.educator = User(id=str(uuid.uuid4()), school_id=self.school.id, email='educator@test.com', role='educator', password_hash='hash', first_name='Educator', last_name='Test')
        self.student = User(id=str(uuid.uuid4()), school_id=self.school.id, email='student@test.com', role='student', password_hash='hash', first_name='Student', last_name='Test')
        self.class_ = Class(id=str(uuid.uuid4()), school_id=self.school.id, name='Class A')
        with app.app_context():
            db.session.add_all([self.school, self.educator, self.student, self.class_])
            db.session.commit()

        self.educator_token = create_access_token(identity=self.educator.id)
        self.student_token = create_access_token(identity=self.student.id)

    def tearDown(self):
        with app.app_context():
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

        # Verify database state
        with app.app_context():
            resource = Resource.query.filter_by(filename='test.txt').first()
            self.assertIsNotNone(resource)
            self.assertEqual(resource.uploaded_by, self.educator.id)

    def test_upload_resource_non_educator(self):
        response = self.client.post(
            f'/schools/{self.school.id}/resources',
            data={'file': (BytesIO(b'Test content'), 'test.txt')},
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json['error'], 'Only educators can upload')

    def test_upload_resource_no_file(self):
        response = self.client.post(
            f'/schools/{self.school.id}/resources',
            content_type='multipart/form-data',
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'No file provided')

    def test_get_resources_educator(self):
        resource = Resource(
            id=str(uuid.uuid4()), school_id=self.school.id, uploaded_by=self.educator.id,
            filename='test.txt', filepath='uploads/test.txt'
        )
        with app.app_context():
            db.session.add(resource)
            db.session.commit()

        response = self.client.get(
            f'/schools/{self.school.id}/resources',
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['filename'], 'test.txt')

    def test_get_resources_student(self):
        resource = Resource(
            id=str(uuid.uuid4()), school_id=self.school.id, uploaded_by=self.educator.id,
            filename='test.txt', filepath='uploads/test.txt'
        )
        permission = ResourcePermission(resource_id=resource.id, class_id=self.class_.id)
        with app.app_context():
            db.session.add_all([resource, permission])
            db.session.commit()

        response = self.client.get(
            f'/schools/{self.school.id}/resources',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['filename'], 'test.txt')

    def test_get_resources_student_no_permission(self):
        resource = Resource(
            id=str(uuid.uuid4()), school_id=self.school.id, uploaded_by=self.educator.id,
            filename='test.txt', filepath='uploads/test.txt'
        )
        with app.app_context():
            db.session.add(resource)
            db.session.commit()

        response = self.client.get(
            f'/schools/{self.school.id}/resources',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

    def test_update_permissions(self):
        resource = Resource(
            id=str(uuid.uuid4()), school_id=self.school.id, uploaded_by=self.educator.id,
            filename='test.txt', filepath='uploads/test.txt'
        )
        with app.app_context():
            db.session.add(resource)
            db.session.commit()

        response = self.client.put(
            f'/resources/{resource.id}/permissions',
            json={'class_ids': [self.class_.id]},
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Permissions updated')

        # Verify database state
        with app.app_context():
            permission = ResourcePermission.query.filter_by(resource_id=resource.id, class_id=self.class_.id).first()
            self.assertIsNotNone(permission)

    def test_update_permissions_invalid_input(self):
        resource = Resource(
            id=str(uuid.uuid4()), school_id=self.school.id, uploaded_by=self.educator.id,
            filename='test.txt', filepath='uploads/test.txt'
        )
        with app.app_context():
            db.session.add(resource)
            db.session.commit()

        response = self.client.put(
            f'/resources/{resource.id}/permissions',
            json={},
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'class_ids required')

    def test_download_resource_educator(self):
        resource = Resource(
            id=str(uuid.uuid4()), school_id=self.school.id, uploaded_by=self.educator.id,
            filename='test.txt', filepath=os.path.join(app.config['UPLOAD_FOLDER'], 'test.txt')
        )
        with app.app_context():
            db.session.add(resource)
            db.session.commit()

        with open(resource.filepath, 'wb') as f:
            f.write(b'Test content')

        response = self.client.get(
            f'/resources/{resource.id}/download',
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Disposition'], f'attachment; filename={resource.filename}')

if __name__ == '__main__':
    unittest.main()