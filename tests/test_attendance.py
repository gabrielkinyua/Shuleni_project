import unittest
from app import create_app, db
from app.models.attendance import Attendance
from app.models.user import User
from app.models.school import School
from app.models.assessment import Class
from flask_jwt_extended import create_access_token
import uuid
from datetime import date

class AttendanceTests(unittest.TestCase):
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
            # Create a class
            self.class_ = Class(id=str(uuid.uuid4()), school_id=self.school.id, name="Class A")
            db.session.add(self.class_)
            # Create users
            self.educator = User(
                id=uuid.uuid4(), school_id=self.school.id, email="educator@test.com",
                password_hash="hashed", role="educator", first_name="Educator", last_name="Test"
            )
            self.student = User(
                id=uuid.uuid4(), school_id=self.school.id, email="student@test.com",
                password_hash="hashed", role="student", first_name="Student", last_name="Test"
            )
            db.session.add_all([self.educator, self.student])
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_take_attendance_success(self):
        with self.app.app_context():
            token = create_access_token(identity=str(self.educator.id))
            response = self.client.post(
                f'/api/schools/{self.school.id}/classes/{self.class_.id}/attendance',
                headers={'Authorization': f'Bearer {token}'},
                json={'attendance_records': [{'student_id': str(self.student.id), 'status': 'present'}]}
            )
            self.assertEqual(response.status_code, 201)

    def test_take_attendance_unauthorized(self):
        with self.app.app_context():
            token = create_access_token(identity=str(self.student.id))
            response = self.client.post(
                f'/api/schools/{self.school.id}/classes/{self.class_.id}/attendance',
                headers={'Authorization': f'Bearer {token}'},
                json={'attendance_records': [{'student_id': str(self.student.id), 'status': 'present'}]}
            )
            self.assertEqual(response.status_code, 403)

    def test_view_attendance(self):
        with self.app.app_context():
            attendance = Attendance(
                id=1, student_id=self.student.id, class_id=self.class_.id,
                date=date.today(), status="present", signed_by=self.educator.id
            )
            db.session.add(attendance)
            db.session.commit()
            token = create_access_token(identity=str(self.educator.id))
            response = self.client.get(
                f'/api/schools/{self.school.id}/classes/{self.class_.id}/attendance',
                headers={'Authorization': f'Bearer {token}'}
            )
            self.assertEqual(response.status_code, 200)

    def test_sign_attendance(self):
        with self.app.app_context():
            attendance = Attendance(
                id=1, student_id=self.student.id, class_id=self.class_.id,
                date=date.today(), status="present", signed_by=self.educator.id
            )
            db.session.add(attendance)
            db.session.commit()
            token = create_access_token(identity=str(self.educator.id))
            response = self.client.put(
                f'/api/attendance/{attendance.id}/sign',
                headers={'Authorization': f'Bearer {token}'}
            )
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()