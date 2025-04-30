import unittest
from app import create_app, db
from app.models.user import User
from app.models.school import School
from app.models.assessment import Class
from app.models.attendance import Attendance
from flask_jwt_extended import create_access_token
from datetime import date

class AttendanceTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/shuleni_test'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Setup test data
            self.school = School(name='Test School')
            db.session.add(self.school)
            self.educator = User(
                school_id=self.school.id, email='educator@test.com', role='educator',
                password_hash='hash', first_name='Educator', last_name='Test'
            )
            self.student = User(
                school_id=self.school.id, email='student@test.com', role='student',
                password_hash='hash', first_name='Student', last_name='Test'
            )
            self.class_ = Class(school_id=self.school.id, name='Class A')
            db.session.add_all([self.educator, self.student, self.class_])
            db.session.commit()

            self.educator_token = create_access_token(identity=self.educator.id)
            self.student_token = create_access_token(identity=self.student.id)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_take_attendance_success(self):
        response = self.client.post(
            f'/api/schools/{self.school.id}/classes/{self.class_.id}/attendance',
            json={
                'attendance_records': [
                    {'student_id': self.student.id, 'status': 'present'}
                ]
            },
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.json['records']), 1)
        self.assertEqual(response.json['records'][0]['status'], 'present')

    def test_take_attendance_unauthorized(self):
        response = self.client.post(
            f'/api/schools/{self.school.id}/classes/{self.class_.id}/attendance',
            json={
                'attendance_records': [
                    {'student_id': self.student.id, 'status': 'present'}
                ]
            },
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        self.assertEqual(response.status_code, 403)

    def test_view_attendance(self):
        with self.app.app_context():
            attendance = Attendance(
                student_id=self.student.id, class_id=self.class_.id,
                date=date.today(), status='present', signed_by=None
            )
            db.session.add(attendance)
            db.session.commit()

        response = self.client.get(
            f'/api/schools/{self.school.id}/classes/{self.class_.id}/attendance',
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['status'], 'present')

    def test_sign_attendance(self):
        with self.app.app_context():
            attendance = Attendance(
                student_id=self.student.id, class_id=self.class_.id,
                date=date.today(), status='present', signed_by=None
            )
            db.session.add(attendance)
            db.session.commit()
            attendance_id = attendance.id

        response = self.client.put(
            f'/api/attendance/{attendance_id}/sign',
            headers={'Authorization': f'Bearer {self.educator_token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['attendance']['signed_by'], self.educator.id)

if __name__ == '__main__':
    unittest.main()