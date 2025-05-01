# from flask_sqlalchemy import SQLAlchemy
# import uuid

# db = SQLAlchemy()

# class School(db.Model):
#     id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
#     name = db.Column(db.String(100), nullable=False)

# class User(db.Model):
#     id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
#     school_id = db.Column(db.String(36), db.ForeignKey('school.id'), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     role = db.Column(db.String(20), nullable=False)  # owner/manager, educator, student

# class Class(db.Model):
#     id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
#     school_id = db.Column(db.String(36), db.ForeignKey('school.id'), nullable=False)
#     name = db.Column(db.String(100), nullable=False)

# class Resource(db.Model):
#     id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
#     school_id = db.Column(db.String(36), db.ForeignKey('school.id'), nullable=False)
#     uploaded_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
#     filename = db.Column(db.String(200), nullable=False)
#     filepath = db.Column(db.String(300), nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
#     __table_args__ = (db.Index('idx_resource_school_id', 'school_id'),)

# class ResourcePermission(db.Model):
#     id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
#     resource_id = db.Column(db.String(36), db.ForeignKey('resource.id'), nullable=False)
#     class_id = db.Column(db.String(36), db.ForeignKey('class.id'), nullable=False)
#     __table_args__ = (db.Index('idx_resource_permission_resource_id', 'resource_id'),)