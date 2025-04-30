import unittest
from app import create_app, db
from app.models.assessment import Assessment, Question, Submission, Answer
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta

class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/shuleni_test'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_assessment(self):
        token = create_access_token(identity="1")
        response = self.client.post(
            '/api/schools/1/assessments',
            json={
                'title': 'Math Test',
                'duration': 60,
                'questions': [{'text': 'What is 2+2?', 'type': 'multiple_choice', 'max_score': 10}]
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['title'], 'Math Test')

    def test_edit_assessment(self):
        with self.app.app_context():
            assessment = Assessment(school_id=1, title='Math Test', duration=60)
            db.session.add(assessment)
            db.session.commit()
            assessment_id = assessment.id

        token = create_access_token(identity="1")
        response = self.client.put(
            f'/api/assessments/{assessment_id}',
            json={'title': 'Updated Math Test', 'duration': 90},
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], 'Updated Math Test')

    def test_start_assessment(self):
        with self.app.app_context():
            assessment = Assessment(school_id=1, title='Math Test', duration=60)
            db.session.add(assessment)
            db.session.commit()
            assessment_id = assessment.id

        token = create_access_token(identity="1")
        response = self.client.post(
            f'/api/assessments/{assessment_id}/start',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('submission_id', response.json)

    def test_submit_assessment_with_plagiarism(self):
        with self.app.app_context():
            assessment = Assessment(school_id=1, title='Math Test', duration=60)
            db.session.add(assessment)
            db.session.flush()
            question = Question(assessment_id=assessment.id, text='What is 2+2?', question_type='essay', max_score=10)
            db.session.add(question)
            submission = Submission(assessment_id=assessment.id, student_id=1)
            db.session.add(submission)
            db.session.commit()
            submission_id = submission.id
            question_id = question.id

        token = create_access_token(identity="1")
        response = self.client.post(
            f'/api/assessments/{assessment.id}/submit',
            json={
                'submission_id': submission_id,
                'answers': [
                    {'question_id': question_id, 'text': 'This is a test answer.'},
                    {'question_id': question_id, 'text': 'This is a test answer.'}
                ]
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['plagiarism_flag'])

    def test_view_results(self):
        with self.app.app_context():
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
            assessment_id = assessment.id

        token = create_access_token(identity="1")
        response = self.client.get(
            f'/api/assessments/{assessment_id}/results',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['score'], 8.0)
        self.assertEqual(len(response.json['answers']), 1)

if __name__ == '__main__':
    unittest.main()