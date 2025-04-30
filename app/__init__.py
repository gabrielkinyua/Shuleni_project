from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from app.routes.school_routes import bp as school_routes
    from app.routes.user_routes import bp as user_routes
    from app.routes.assessments import assessments_bp
    from app.endpoints import resource_bp

    app.register_blueprint(school_routes, url_prefix='/api')
    app.register_blueprint(user_routes, url_prefix='/api')
    app.register_blueprint(assessments_bp, url_prefix='/api')
    app.register_blueprint(resource_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app