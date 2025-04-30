from app.models import db
from datetime import datetime
import uuid

class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='school', lazy=True)