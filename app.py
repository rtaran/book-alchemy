from flask import Flask
from data_models import db, Author, Book  # Import database and models
import os

# Initialize Flask app with a custom instance path
app = Flask(__name__, instance_path=os.path.abspath("data"))

# Ensure the instance directory exists
os.makedirs(app.instance_path, exist_ok=True)

# Configure the SQLite database URI to be within the instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "library.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Create database tables (run once, then comment out)
# with app.app_context():
#     db.create_all()
#     print("✅ Database tables created successfully!")

if __name__ == "__main__":
    app.run(debug=True)