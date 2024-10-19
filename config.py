import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "I-Hope-This-Is-Secure"
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost/Spheres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False