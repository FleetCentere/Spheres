import os
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost/Spheres"

from datetime import datetime, timezone, timedelta
import unittest
from app import app, db
from app.models import User, Post