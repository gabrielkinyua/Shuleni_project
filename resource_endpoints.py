from flask import Blueprint, request, jsonify
from app.models.resource import Resource
from app.models.class_ import Class
from app.models.user import User
from app import db 
from datetime import datetime

resource_bp = Blueprint('resource', __name__)

#Upload a file to class
@resource_bp.route('/classes/<int:class_id>/resources', methods=['POST'])
@jwt_requried()
def upload_resource(class_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id) 

#Check if the user is an educator and belongs to the schools class
    class_ = Class.query.get_or_404(class_id)
if user.role != 'educator' or user.school_id != class_.school_id:
    return jsonify({'error': 'Unauthorized'}), 404

file = request.files['file']
permissions = request.form.get('permissions', 'class')

# try:
#     file_url = upload_file_to_s3(file, class_id)
# expect Exception as e:
#     return jsonify({'error': f'File upload failed: {str(e)}'}), 500

    resource = Resource(
    school_id=user.school_id,
    class_id=class_id,
    file_name=file.filename,
    file_url=file_url,
    uploaded_by=user_id,
    permissions=permissions
)
db.session.add(resource)
db.session.commit()

return jsonify(resource.to_dict()), 201

@resource_bp.route('classes/<int:class_id>/resources', methods=['GET'])
@jwt_requried()
def list_resources(class_id):
    user_id = get_jwt_identify()
    user = User.query.get(user_id)

    #Check if user belongs to the class
    class_ = Class.query.get_or_404(class_id)
    if user.school_id != class_.school_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    #Get resources 
    resources = Resource.query.filter_by(class_id=class_id).all()
    if user.role == 'student':
        resources = [r for r in resource if r.permission == 'class']

    return jsonify([r.to_dict() for r in resources]), 200