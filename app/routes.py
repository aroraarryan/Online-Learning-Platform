from app import app
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('base.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find user by email from the database
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):  # Check password hash
            flash("Login successful!", "success")
            if user.role == "student":
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('instructor_dashboard'))  # Redirect to instructor dashboard
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template('login.html')

@bp.route('/student_dashboard')
def student_dashboard():
    return "<h1>Welcome to your Student Dashboard!</h1>"

@bp.route('/instructor_dashboard')
def instructor_dashboard():
    return "<h1>Welcome to your Instructor Dashboard!</h1>"
