from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    Author model representing book authors in the database.

    Attributes:
        id: Primary key for the author
        name: Author's full name
        birth_date: Author's date of birth
        date_of_death: Author's date of death (if applicable)
        nationality: Author's nationality
        books: Relationship to the author's books
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)
    nationality = db.Column(db.String(50))  # Keep this line
    books = db.relationship('Book', back_populates='author', cascade='all, delete-orphan')

    def __repr__(self):
        """Return a string representation of the Author object."""
        return f"<Author {self.name}>"


class Book(db.Model):
    """
    Book model representing books in the database.

    Attributes:
        id: Primary key for the book
        isbn: International Standard Book Number
        title: Book title
        publication_year: Year the book was published
        rating: Book rating (0-5)
        author_id: Foreign key to the author
        author: Relationship to the book's author
    """
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(17), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer)
    rating = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        """Return a string representation of the Book object."""
        return f"<Book {self.title}>"
