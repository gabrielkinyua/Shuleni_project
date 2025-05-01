import unittest
from app import create_app, db
from app.models.assessment import Assessment, Class, Question,Submission
from app.models.school import School
from flask_jwt_extended import create_access_token
import uuid

class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://shuleni_user:binarybrains@localhost/shuleni_test'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create a school
            self.school = School(id=uuid.uuid4(), name="Test School")
            db.session.add(self.school)
            # Create a class (not used in Assessment, but for consistency)
            self.class_id = str(uuid.uuid4())
            class_ = Class(id=self.class_id, school_id=self.school.id, name="Class A")
            db.session.add(class_)
            db.session.commit()
            self.school_id = str(self.school.id)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    

    def test_create_assessment(self):
        with self.app.app_context():
            token = create_access_token(identity=str(uuid.uuid4()))
            response = self.client.post(
                f'/api/assessments/schools/{self.school_id}/assessments',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'title': 'Math Test',
                    'duration': 60,
                    'questions': [{'text': 'What is 2+2?', 'type': 'multiple_choice', 'max_score': 10}]
                }
            )
            self.assertEqual(response.status_code, 201)

    def test_edit_assessment(self):
        with self.app.app_context():
            assessment = Assessment(id=uuid.uuid4(), school_id=self.school_id, title='Math Test', duration=60)
            db.session.add(assessment)
            db.session.commit()
            token = create_access_token(identity=str(uuid.uuid4()))
            response = self.client.put(
                f'/api/assessments/assessments/{assessment.id}',
                headers={'Authorization': f'Bearer {token}'},
                json={'title': 'Updated Math Test'}
            )
            self.assertEqual(response.status_code, 200)

    def test_start_assessment(self):
        with self.app.app_context():
            assessment = Assessment(id=uuid.uuid4(), school_id=self.school_id, title='Math Test', duration=60)
            db.session.add(assessment)
            db.session.commit()
            token = create_access_token(identity=str(uuid.uuid4()))
            response = self.client.post(
                f'/api/assessments/assessments/{assessment.id}/start',
                headers={'Authorization': f'Bearer {token}'}
            )
            self.assertEqual(response.status_code, 200)

    def test_submit_assessment_with_plagiarism(self):
        with self.app.app_context():
            assessment = Assessment(id=uuid.uuid4(), school_id=self.school_id, title='Math Test', duration=60)
            question = Question(id=uuid.uuid4(), assessment_id=assessment.id, text='What is 2+2?', question_type='text', max_score=10)
            db.session.add_all([assessment, question])
            db.session.commit()
            submission = Submission(id=uuid.uuid4(), assessment_id=assessment.id, student_id=str(uuid.uuid4()))
            db.session.add(submission)
            db.session.commit()
            token = create_access_token(identity=str(submission.student_id))
            response = self.client.post(
                f'/api/assessments/assessments/{assessment.id}/submit',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'submission_id': str(submission.id),
                    'answers': [{'question_id': str(question.id), 'text': 'Answer'}]
                }
            )
            self.assertEqual(response.status_code, 200)

    def test_view_results(self):
        with self.app.app_context():
            assessment = Assessment(id=uuid.uuid4(), school_id=self.school_id, title='Math Test', duration=60)
            student_id = str(uuid.uuid4())
            submission = Submission(id=uuid.uuid4(), assessment_id=assessment.id, student_id=student_id)
            db.session.add_all([assessment, submission])
            db.session.commit()
            token = create_access_token(identity=student_id)
            response = self.client.get(
                f'/api/assessments/assessments/{assessment.id}/results',
                headers={'Authorization': f'Bearer {token}'}
            )
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()