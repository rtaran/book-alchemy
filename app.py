from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book  # Importing the database and models (will be created next)

# Initialize Flask app
app = Flask(__name__)

# Set database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppresses a warning

# Connect Flask app to the database
db.init_app(app)

# Ensure database tables are created
with app.app_context():
    db.create_all()