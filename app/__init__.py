from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configure app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    # Initialize the database with the app
    db.init_app(app)

    # Import routes (views) after app and db are initialized
    from . import routes

    # Register blueprints or routes
    app.register_blueprint(routes.bp)

    return app
