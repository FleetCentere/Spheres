import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "I-Hope-This-Is-Secure"
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost/spheres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False