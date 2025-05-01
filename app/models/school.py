from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


class School(db.Model):
    __tablename__ = 'schools'
    # id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='school', lazy=True)
