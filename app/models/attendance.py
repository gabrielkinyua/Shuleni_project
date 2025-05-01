from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    signed_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('User', foreign_keys=[student_id], backref='attendance')
    class_ = db.relationship('Class', backref='attendance_records')
    signer = db.relationship('User', foreign_keys=[signed_by], backref='signed_attendance')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'class_id': self.class_id,
            'date': self.date.isoformat(),
            'status': self.status,
            'signed_by': self.signed_by,
            'created_at': self.created_at.isoformat()
        }