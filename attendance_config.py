import os 
from dotev import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5555/school_db')