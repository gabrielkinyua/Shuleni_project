from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = db.Column(UUID(as_uuid=True), db.ForeignKey('schools.id'), nullable=False)
    uploaded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    school = db.relationship('School', backref='resources')
    uploader = db.relationship('User', backref='resources')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'filepath': self.filepath,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat()
        }