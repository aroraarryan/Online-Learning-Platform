import eventlet
eventlet.monkey_patch()
import openai
from flask import Flask, render_template, request, redirect, url_for, flash,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit
from eventlet import wsgi
import eventlet.wsgi
from flask_cors import CORS
import requests
import json
import os
# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Initialize the database
users = {
    "student_user": {"password": "student_password", "role": "student"},
    "instructor_user": {"password": "instructor_password", "role": "instructor"},
}
JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), "courses.json")
@app.route('/courses', methods=['GET'])
def get_courses():
    """Fetch all courses from the JSON file."""
    try:
        with open(JSON_FILE_PATH, 'r') as file:
            courses = json.load(file)
        return jsonify(courses)
    except FileNotFoundError:
        return jsonify({"error": "Courses file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500
@app.route('/search_course', methods=['GET'])
def search_course():
    """Search for a course by title."""
    course_title = request.args.get('title', '').lower()
    try:
        with open(JSON_FILE_PATH, 'r') as f:
            courses_data = json.load(f)
        course = next((c for c in courses_data if c['title'].lower() == course_title), None)
        if course:
            return jsonify(course)
        else:
            return jsonify({"error": "Course not found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Route for the home page
@app.route('/')
def home():
    return render_template('base.html')
# Route for the about page
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/courses_home')
def courses_home():
    return render_template('courses_home.html')
@app.route('/todolist')
def todolist():
    return render_template('todolist.html')

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        # Get the JSON data from the POST request
        data = request.get_json()  # Use .get_json() to parse JSON data
        user_message = data.get('message')  # Extract the message from the JSON data
        
        try:
            # Make the API request to OpenAI
            response = openai.Completion.create(
                engine="text-davinci-003",  # Or another OpenAI model
                prompt=user_message,  # Pass the user's message to the OpenAI API
                max_tokens=150  # Limit the length of the generated response
            )

            chatbot_reply = response.choices[0].text.strip()  # Extract the response text
            return jsonify({'response': chatbot_reply})  # Return the response to the frontend
        except Exception as e:
            print(f"Error: {e}")  # Log error details
            return jsonify({'response': "Sorry, I'm having trouble responding right now."})  # Handle errors
    return render_template('chatbot.html')  # Render the chatbot page for GET requests


@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/timer')
def timer():
    return render_template('timer.html')

# Route for the courses page
@app.route('/courses')
def courses():
    return render_template('courses.html')
@app.route('/my_courses')
def my_courses():
    return render_template('my_courses.html')
# Route for the 'Get Started' page
@app.route('/get_started')
def get_started():
    return render_template('get_started.html')
@app.route('/GAME')
def GAME():
    return render_template('GAME.html')
@app.route('/my_activities')
def my_activities():
    return render_template('my_activities.html')
@app.route('/maths_flashcards')
def maths_flashcards():
    return render_template('maths_flashcards.html')
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')
@app.route('/WORDScrable')
def WORDSCRABLE():
    return render_template('WORDSCRABLE.HTML')
# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}', '{self.role}')"

@app.route('/login', methods=['GET', 'POST'])
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
@app.route('/instructor_login', methods=['GET', 'POST'])
def instructor_login():
    # Your logic for instructor login
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find user by email from the database
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):  # Check password hash
            flash("Login successful!", "success")
            if user.role == "instructor":
                return redirect(url_for('instructor_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))  # Redirect to instructor dashboard
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template('instructor_login.html')


# Route for the new user registration page

@app.route('/new_user', methods=['GET', 'POST'])

def new_user():
    error_message = None  # Initialize error message as None
    success_message = None  # Initialize success message as None

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # 'student' or 'instructor'

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error_message = "This email is already registered. Please use a different email."
            return render_template('new_user.html', error_message=error_message)  # Show the error message on the form

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new user
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        success_message = "New user created successfully!"
        
        # Redirect based on the role of the user
        if role == 'instructor':
            return render_template('instructor_login.html', success_message=success_message)  # Show the success message on the form
        else:
            return render_template('login.html', success_message=success_message)  # Show success message on the form

    return render_template('new_user.html', error_message=error_message, success_message=success_message) # Render the user creation page


# Route for the student dashboard (after login)
@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

# Route for the instructor dashboard (after login)
@app.route('/instructor_dashboard')
def instructor_dashboard():
    return render_template('instructor_dashboard.html')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
from werkzeug.security import generate_password_hash


@socketio.on('send_notification')
def handle_notification(data):
    # Emit the message to all connected clients
    emit('receive_notification', {'message': data['message']}, broadcast=True)

# Emit notification on a specific route (e.g., when a user logs in or completes an action)
@app.route('/send_notification')
def send_notification():
    message = "You have a new notification!"
    socketio.emit('receive_notification', {'message': message}, broadcast=True)
    return "Notification sent!"

# Listen for login success and send notifications on the client side
@app.route('/notify_student')
def notify_student():
    socketio.emit('receive_notification', {'message': 'You have a new message from your instructor!'}, room='student')
    return "Notification sent to student!"
@socketio.on('connect')
def handle_connect():
    print("A user connected!")
@app.route('/notifications')
def get_notifications():
    # Fetch notifications from your database or any source
    notifications = [
        "This is Your Notification Bar",
        "Latest notifications will be updated here."
    ]
    return jsonify(notifications)
# Start the Flask app with SocketIO
if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
    