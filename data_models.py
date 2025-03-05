from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)
    nationality = db.Column(db.String(50))  # Keep this line
    books = db.relationship('Book', backref='author', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Author {self.name}>"

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(17), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer)
    rating = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))

    def __repr__(self):
        return f"<Book {self.title}>"