from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('schools.id'), nullable=False)
    uploaded_by = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    permissions = db.relationship('ResourcePermission', backref='resource_obj', lazy=True)  # Changed backref
    school = db.relationship('School', backref='resources')
    uploader = db.relationship('User', backref='resources')

    def to_dict(self):
        return {
            'id': str(self.id),
            'file_name': self.file_name,
            'file_path': self.file_path,
            'uploaded_by': str(self.uploaded_by),
            'uploaded_at': self.uploaded_at.isoformat(),
            'school_id': str(self.school_id)
        }