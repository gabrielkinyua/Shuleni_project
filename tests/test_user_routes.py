import unittest
from app import create_app, db
from app.models.user import User
from app.models.school import School
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

class UserRoutesTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/shuleni_test'
        with self.app.app_context():
            db.create_all()
            yield self.app
            db.session.remove()
            db.drop_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_user_success(self):
        school = School(name='Test School')
        db.session.add(school)
        
        owner = User(
            school_id=school.id,
            email='owner@test.com',
            password_hash=generate_password_hash('password'),
            role='owner',
            first_name='Test',
            last_name='Owner'
        )
        db.session.add(owner)
        db.session.commit()
        
        token = create_access_token(identity=owner.id)
        
        response = self.app.test_client().post(
            f'/api/schools/{school.id}/users',
            json={
                'email': 'student@test.com',
                'password': 'password',
                'role': 'student',
                'first_name': 'Test',
                'last_name': 'Student'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['email'], 'student@test.com')
        self.assertEqual(response.json['role'], 'student')

    def test_add_user_invalid_role(self):
        school = School(name='Test School')
        db.session.add(school)
        
        owner = User(
            school_id=school.id,
            email='owner@test.com',
            password_hash=generate_password_hash('password'),
            role='owner',
            first_name='Test',
            last_name='Owner'
        )
        db.session.add(owner)
        db.session.commit()
        
        token = create_access_token(identity=owner.id)
        
        response = self.app.test_client().post(
            f'/api/schools/{school.id}/users',
            json={
                'email': 'student@test.com',
                'password': 'password',
                'role': 'invalid',
                'first_name': 'Test',
                'last_name': 'Student'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Invalid role')

    def test_update_user_success(self):
        school = School(name='Test School')
        db.session.add(school)
        
        owner = User(
            school_id=school.id,
            email='owner@test.com',
            password_hash=generate_password_hash('password'),
            role='owner',
            first_name='Test',
            last_name='Owner'
        )
        user = User(
            school_id=school.id,
            email='student@test.com',
            password_hash=generate_password_hash('password'),
            role='student',
            first_name='Test',
            last_name='Student'
        )
        db.session.add_all([owner, user])
        db.session.commit()
        
        token = create_access_token(identity=owner.id)
        
        response = self.app.test_client().put(
            f'/api/users/{user.id}',
            json={'email': 'newstudent@test.com', 'first_name': 'New'},
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], 'newstudent@test.com')
        self.assertEqual(response.json['first_name'], 'New')

    def test_delete_user_success(self):
        school = School(name='Test School')
        db.session.add(school)
        
        owner = User(
            school_id=school.id,
            email='owner@test.com',
            password_hash=generate_password_hash('password'),
            role='owner',
            first_name='Test',
            last_name='Owner'
        )
        user = User(
            school_id=school.id,
            email='student@test.com',
            password_hash=generate_password_hash('password'),
            role='student',
            first_name='Test',
            last_name='Student'
        )
        db.session.add_all([owner, user])
        db.session.commit()
        
        token = create_access_token(identity=owner.id)
        
        response = self.app.test_client().delete(
            f'/api/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'User deleted')

if __name__ == '__main__':
    unittest.main()