from flask import Blueprint, request, jsonify
from app.models.user import User 
from app import db
from datetime import datetime

resource_bp = Blueprint('resource', __name__)

#this document will house the endpoints for attendence 