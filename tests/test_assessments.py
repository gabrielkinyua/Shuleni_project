import pytest
from app import create_app, db
from app.models.assessment import Assessment, Question, Submission, Answer
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://shuleni_user:securepassword@localhost:5432/shuleni_test'
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture
def token():
    with create_app().app_context():
        return create_access_token(identity=1)

def test_create_assessment(client, token):
    response = client.post(
        '/api/schools/1/assessments',
        json={
            'title': 'Math Test',
            'duration': 60,
            'questions': [{'text': 'What is 2+2?', 'type': 'multiple_choice', 'max_score': 10}]
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['title'] == 'Math Test'

def test_edit_assessment(client, token):

    assessment = Assessment(school_id=1, title='Math Test', duration=60)
    db.session.add(assessment)
    db.session.commit()

    response = client.put(
        f'/api/assessments/{assessment.id}',
        json={'title': 'Updated Math Test', 'duration': 90},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json['title'] == 'Updated Math Test'

def test_start_assessment(client, token):
    assessment = Assessment(school_id=1, title='Math Test', duration=60)
    db.session.add(assessment)
    db.session.commit()

    response = client.post(
        f'/api/assessments/{assessment.id}/start',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert 'submission_id' in response.json

def test_submit_assessment_with_plagiarism(client, token):

    assessment = Assessment(school_id=1, title='Math Test', duration=60)
    db.session.add(assessment)
    db.session.flush()
    question = Question(assessment_id=assessment.id, text='What is 2+2?', question_type='essay', max_score=10)
    db.session.add(question)
    submission = Submission(assessment_id=assessment.id, student_id=1)
    db.session.add(submission)
    db.session.commit()

    response = client.post(
        f'/api/assessments/{assessment.id}/submit',
        json={
            'submission_id': submission.id,
            'answers': [
                {'question_id': question.id, 'text': 'This is a test answer.'},
                {'question_id': question.id, 'text': 'This is a test answer.'}
            ]
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json['plagiarism_flag'] is True

def test_view_results(client, token):

    assessment = Assessment(school_id=1, title='Math Test', duration=60)
    db.session.add(assessment)
    db.session.flush()
    question = Question(assessment_id=assessment.id, text='What is 2+2?', question_type='essay', max_score=10)
    db.session.add(question)
    submission = Submission(assessment_id=assessment.id, student_id=1, score=8.0)
    db.session.add(submission)
    db.session.flush()
    answer = Answer(submission_id=submission.id, question_id=question.id, text='Answer', score=8.0)
    db.session.add(answer)
    db.session.commit()

    response = client.get(
        f'/api/assessments/{assessment.id}/results',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json['score'] == 8.0
    assert len(response.json['answers']) == 1