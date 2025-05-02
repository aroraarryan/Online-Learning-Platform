from . import db  # Import db from __init__.py (which initializes the SQLAlchemy instance)
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    # Relationship to UserActivity (One-to-Many)
    activities = db.relationship('UserActivity', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}', '{self.role}')"


class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)  # e.g., "Course Completed"
    activity_description = db.Column(db.String(255), nullable=False)  # e.g., "Completed Python Basics"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Back reference to User model
    user = db.relationship('User', back_populates='activities')

    def __repr__(self):
        return f'<Activity {self.activity_type} - {self.activity_description}>'

