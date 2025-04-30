from app.endpoints import db 
from datetime import datetime 

class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permissions = db.Column(db.String(50), defaults='class')
    created_at = db.Column(db.Datetime, default=datetime.utcnow)

    school = db.relationship('School', backref='resources')
    class_ = db.relationship('Class', backref='resources')
    uploader = db.relationship('User', backref='resources')

    def to_dict(self):
        return {
            'id' :self.id,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'class_id': self.class_id,
            'uploaded_by': self.uploaded_by,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat()
        }