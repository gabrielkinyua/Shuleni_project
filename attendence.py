from app.endpoints import db 
from datetime import datetime 

class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    signed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.Datetime, default=datetime.utcnow )

    student = db.relationship('User', foreign_keys=[student_id], backref='attendance')
    class_ = db.relationship('Class', backref='resources')
    signer = db.relationship('User', foreign_keys=[signed_by], backref='resources')

    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'class_id': self.class_id,
            'uploaded_by': self.uploaded_by,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat()
        }