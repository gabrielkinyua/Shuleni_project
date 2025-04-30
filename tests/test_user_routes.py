import pytest
from app import create_app, db
from app.models.user import User
from app.models.school import School
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/shuleni_test'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_add_user_success(client):
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
    
    response = client.post(
        f'/schools/{school.id}/users',
        json={
            'email': 'student@test.com',
            'password': 'password',
            'role': 'student',
            'first_name': 'Test',
            'last_name': 'Student'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 201
    assert response.json['email'] == 'student@test.com'
    assert response.json['role'] == 'student'

def test_add_user_invalid_role(client):
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
    
    response = client.post(
        f'/schools/{school.id}/users',
        json={
            'email': 'student@test.com',
            'password': 'password',
            'role': 'invalid',
            'first_name': 'Test',
            'last_name': 'Student'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid role'

def test_update_user_success(client):
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
    
    response = client.put(
        f'/users/{user.id}',
        json={'email': 'newstudent@test.com', 'first_name': 'New'},
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    assert response.json['email'] == 'newstudent@test.com'
    assert response.json['first_name'] == 'New'

def test_delete_user_success(client):
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
    
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    assert response.json['message'] == 'User deleted'