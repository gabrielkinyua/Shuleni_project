from app.models import db
from datetime import datetime

class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
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