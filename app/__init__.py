feature/online-assessments
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


    from app.routes.assessments import assessments_bp
    app.register_blueprint(assessments_bp, url_prefix='/api')
    from .routes import school_routes, user_routes
    app.register_blueprint(school_routes.bp)
    app.register_blueprint(user_routes.bp)
    
    with app.app_context():
        db.create_all()
      main
    return app
