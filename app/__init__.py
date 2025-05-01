from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    print("Loading Config:", Config)
    app.config.from_object(Config)
    print("SQLALCHEMY_DATABASE_URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))
    
    db.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        # Import models
        from .models.school import School
        from .models.user import User
        from .models.resource import Resource  
        from .models.attendance import Attendance
        from .models.assessment import Assessment, Question, Submission, Answer, Class, ResourcePermission
        
        # Import blueprints
        from .routes import school_routes, user_routes
        from .routes.assessments import bp as assessments
        
        # Register blueprints with URL prefixes
        app.register_blueprint(school_routes, url_prefix='/api')
        app.register_blueprint(user_routes, url_prefix='/api')
        app.register_blueprint(assessments, url_prefix='/api/assessments')
        
        db.create_all()
    
    return app