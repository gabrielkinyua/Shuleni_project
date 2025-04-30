from flask import Blueprint, request, jsonify 
from app.models.attendance import Attendance
from app.models.class_ import Class
from app import db
from datetime import datetime, date

attendance_bp = Blueprint('attendance', __name__)

# Marks class attendance
@attendance_bp.route('classes/<int:class_id>/attendance', methods=['POST'])
@jwt_requried()
def mark_attendance(class_id):
    user_id = get_jwt_identify()
    user = User.query.get(user_id)

    # Check if the user is an educator and belongs in the class
    class_ = Class.query.get_or_404(class_id)
    if user.role != 'educator' or user.school_id != class_.school_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    attendance_data = data.get('data', data.today().isoformat())
    records = data.get('records') 

    if not records:
        return jsonify({'error': 'No attendance records provided'}) 
    
    for record in records:
        attendance = Attendance(
            class_id=class_id,
            student_id=record['student_id'],
            date=datetime.fromisoformat(attendance_data).date(),
            status=record['status'],
            signed_by=user_id
        )
    db.session.add(attendance)

    db.session.commit()
    return jsonify({'message': 'Attendance recorded'}), 201

# View attendance for a class
@attendance_bp.route('/classes/<int:class_id>/attendance' methods=['GET'])
@jwt_required()
def get_attendance(class_id):
    user_id = get_jwt_identify()
    user = User.query.get(user_id)

    class_ = Class.query.get_or_404(class_id)
    if user.school_id != class_.school_id:
        return jsonify({'error': 'Unauthorized'}), 403

    query = Attendance.query.filter_by(class_id)
    if user.role == 'student':
        query = query.filter_by(student_id=user_id)

        records = query.all()
        return jsonify([r.to_dict() for r in seconds]), 200