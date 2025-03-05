from flask_sqlalchemy import SQLAlchemy

# Initialize database instance
db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'  # Explicit table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    # Relationship: One author can have many books
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return f'<Author {self.name}>'

    def __str__(self):
        return f'{self.name} (Born: {self.birth_date}, Died: {self.date_of_death or "N/A"})'


class Book(db.Model):
    __tablename__ = 'books' # Explicit table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)

    # Foreign key linking each book to an author
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

    def __str__(self):
        return f'"{self.title}" (ISBN: {self.isbn}, Published: {self.publication_year})'