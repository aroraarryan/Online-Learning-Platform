from app import app, db

# Push the application context
with app.app_context():
    # Drop all tables
    db.drop_all()
    print("All tables dropped.")
    
    # Recreate all tables
    db.create_all()
    print("All tables created.")

import os
print(f"Current working directory: {os.getcwd()}")