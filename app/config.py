import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://shuleni_user:binarybrains@localhost/shuleni')
    print("DATABASE_URL:", SQLALCHEMY_DATABASE_URI)  # Debug print
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'binarybrains')
