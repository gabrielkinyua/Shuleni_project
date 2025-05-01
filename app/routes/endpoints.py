from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.attendance import Attendance
from app.models.assessment import Class
from app.utils.auth import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os
from app.models.source import Resource

resource_bp = Blueprint('resource', __name__)

@resource_bp.route('/schools/<school_id>/classes/<class_id>/attendance', methods=['POST'])
@jwt_required()
@role_required('educator')
def take_attendance(school_id, class_id):
    data = request.get_json()
    if not data or 'attendance_records' not in data:
        return jsonify({'error': 'Attendance records required'}), 400

    class_ = Class.query.filter_by(id=class_id, school_id=school_id).first()
    if not class_:
        return jsonify({'error': 'Class not found'}), 404

    educator_id = get_jwt_identity()
    educator = User.query.get(educator_id)
    if educator.school_id != school_id:
        return jsonify({'error': 'Unauthorized'}), 403

    attendance_records = []
    for record in data['attendance_records']:
        student_id = record.get('student_id')
        status = record.get('status')

        if not student_id or not status:
            return jsonify({'error': 'student_id and status required for each record'}), 400

        student = User.query.get(student_id)
        if not student or student.school_id != school_id or student.role != 'student':
            return jsonify({'error': f'Invalid student_id: {student_id}'}), 400

        if status not in ['present', 'absent', 'late']:
            return jsonify({'error': f'Invalid status for student {student_id}'}), 400

        attendance = Attendance(
            student_id=student_id,
            class_id=class_id,
            date=date.today(),
            status=status,
            signed_by=educator_id   # Will be signed later
        )
        attendance_records.append(attendance)

    db.session.add_all(attendance_records)
    db.session.commit()
    return jsonify({'message': 'Attendance recorded', 'records': [r.to_dict() for r in attendance_records]}), 201

@resource_bp.route('/schools/<school_id>/resources', methods=['POST'])
@jwt_required()
@role_required('educator', 'owner')
def upload_resource(school_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    educator_id = get_jwt_identity()
    educator = User.query.get(educator_id)
    if str(educator.school_id) != school_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(filepath)
    
    # Create resource record
    resource = Resource(
        school_id=school_id,
        uploaded_by=educator_id,
        filename=filename,
        filepath=filepath
    )
    
    db.session.add(resource)
    db.session.commit()
    
    return jsonify(resource.to_dict()), 201

@resource_bp.route('/schools/<school_id>/classes/<class_id>/attendance', methods=['GET'])
@jwt_required()
@role_required('educator')
def view_attendance(school_id, class_id):
    educator_id = get_jwt_identity()
    educator = User.query.get(educator_id)
    if educator.school_id != school_id:
        return jsonify({'error': 'Unauthorized'}), 403

    class_ = Class.query.filter_by(id=class_id, school_id=school_id).first()
    if not class_:
        return jsonify({'error': 'Class not found'}), 404

    date_filter = request.args.get('date')
    if date_filter:
        try:
            date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format, use YYYY-MM-DD'}), 400
        attendance_records = Attendance.query.filter_by(class_id=class_id, date=date_filter).all()
    else:
        attendance_records = Attendance.query.filter_by(class_id=class_id).all()

    return jsonify([record.to_dict() for record in attendance_records]), 200

@resource_bp.route('/attendance/<attendance_id>/sign', methods=['PUT'])
@jwt_required()
@role_required('educator')
def sign_attendance(attendance_id):
    attendance = Attendance.query.get_or_404(attendance_id)
    educator_id = get_jwt_identity()
    educator = User.query.get(educator_id)

    class_ = Class.query.get(attendance.class_id)
    if educator.school_id != class_.school_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if attendance.signed_by:
        return jsonify({'error': 'Attendance already signed'}), 400

    attendance.signed_by = educator_id
    db.session.commit()
    return jsonify({'message': 'Attendance signed', 'attendance': attendance.to_dict()}), 200