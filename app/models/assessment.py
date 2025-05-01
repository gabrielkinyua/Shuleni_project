from app import db
from datetime import datetime
import uuid

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    school = db.relationship('School', backref='assessments')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    assessment = db.relationship('Assessment', backref='questions')

class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    plagiarism_flag = db.Column(db.Boolean, default=False)
    assessment = db.relationship('Assessment', backref='submissions')
    student = db.relationship('User', backref='submissions')

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, default=0)
    submission = db.relationship('Submission', backref='answers')
    question = db.relationship('Question', backref='answers')

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    school = db.relationship('School', backref='classes')

class ResourcePermission(db.Model):
    __tablename__ = 'resource_permissions'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id = db.Column(db.String(36), db.ForeignKey('resources.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id'), nullable=False)
    resource = db.relationship('Resource', backref='permissions')
    class_ = db.relationship('Class', backref='permissions')