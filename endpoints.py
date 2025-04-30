from flask import Blueprint, request, jsonify
from app.models.user import User 
from app
from app import db
from datetime import datetime

resource_bp = Blueprint('resource', __name__)

# Upload a file to class
@resource_bp.route('classes/<int:class_id/resources', methods=['POST'])
@jwt_required()
def upload_resource(class_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

# check if the user is a teacher and belongs to the class's school
    class_ = Class.query.get_or_404(class_id)
    if user.role != 'educator' or user.school_id != class_.school_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
#checks if a file has been sent
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    permission = request.form.get('permissions', 'class')



# save files metadata to the database 
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
#this document will house the endpoints for attendence 