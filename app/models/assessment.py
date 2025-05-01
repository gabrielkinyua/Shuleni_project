from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(UUID(as_uuid=True), db.ForeignKey('schools.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    school = db.relationship('School', backref='classes')

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    class_ = db.relationship('Class', backref='assessments')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assessments.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assessment = db.relationship('Assessment', backref='questions')

class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('assessments.id'), nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    assessment = db.relationship('Assessment', backref='submissions')
    student = db.relationship('User', backref='submissions')

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = db.Column(UUID(as_uuid=True), db.ForeignKey('submissions.id'), nullable=False)
    question_id = db.Column(UUID(as_uuid=True), db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    submission = db.relationship('Submission', backref='answers')
    question = db.relationship('Question', backref='answers')

class ResourcePermission(db.Model):
    __tablename__ = 'resource_permissions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id = db.Column(UUID(as_uuid=True), db.ForeignKey('resources.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id'), nullable=False)
    resource = db.relationship('Resource', backref='permissions')
    class_ = db.relationship('Class', backref='resource_permissions')