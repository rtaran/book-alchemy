from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from data_models import db, Author, Book
from sqlalchemy import or_
import os
from dotenv import load_dotenv
from datetime import datetime
from flask_migrate import Migrate
from datetime import date
load_dotenv()

# Configure absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'data', 'library.sqlite')

# Create data directory if it doesn't exist
if not os.path.exists(os.path.dirname(database_path)):
    os.makedirs(os.path.dirname(database_path))

app = Flask(__name__)
# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)
# Routes
@app.route('/')
def home():
    search_term = request.args.get('q', '')
    sort_by = request.args.get('sort', 'title')

    query = Book.query.join(Author)

    if search_term:
        query = query.filter(or_(
            Book.title.ilike(f'%{search_term}%'),
            Author.name.ilike(f'%{search_term}%')
        ))

    books = query.order_by(Author.name if sort_by == 'author' else Book.title).all()

    return render_template('home.html', books=books, search_term=search_term, sort_by=sort_by)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        try:
            # Convert date strings to Python date objects
            birth_date = None
            if request.form['birth_date']:
                birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()

            date_of_death = None
            if request.form.get('date_of_death'):
                date_of_death = datetime.strptime(request.form['date_of_death'], '%Y-%m-%d').date()

            author = Author(
                name=request.form['name'],
                birth_date=birth_date,
                date_of_death=date_of_death,
                nationality=request.form.get('nationality', None))

            db.session.add(author)
            db.session.commit()
            flash('Author added successfully!', 'success')
            return redirect(url_for('add_author'))

        except ValueError as e:
            flash(f'Invalid date format: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Error adding author: {str(e)}', 'danger')

    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        try:
            book = Book(
                isbn=request.form['isbn'],
                title=request.form['title'],
                publication_year=request.form['publication_year'],
                rating=request.form.get('rating', 0),
                author_id=request.form['author_id']
            )

            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('add_book'))

        except IntegrityError as e:
            db.session.rollback()  # Reset the session
            flash('Error: This ISBN already exists in the database!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding book: {str(e)}', 'danger')

    return render_template('add_book.html', authors=authors)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash(f'Author {author.name} and all their books deleted!', 'success')
    return redirect(url_for('home'))

@app.route('/recommend')
def recommend_books():  # This function name determines the endpoint
    # ... recommendation logic ...
    return render_template('recommendations.html')

def add_sample_books():
    with app.app_context():
        # Check if books already exist
        if Book.query.count() > 0:
            print("Books already exist in database")
            return

        # Create authors
        authors = [
            Author(name="George Orwell", birth_date=date(1903, 6, 25), date_of_death=date(1950, 1, 21),
                   nationality="British"),
            Author(name="Harper Lee", birth_date=date(1926, 4, 28), date_of_death=date(2016, 2, 19),
                   nationality="American"),
            Author(name="F. Scott Fitzgerald", birth_date=date(1896, 9, 24), date_of_death=date(1940, 12, 21),
                   nationality="American"),
            Author(name="Jane Austen", birth_date=date(1775, 12, 16), date_of_death=date(1817, 7, 18),
                   nationality="British")
        ]

        db.session.bulk_save_objects(authors)
        db.session.commit()

        # Create books
        books = [
            Book(title="1984", isbn="9780451524935", publication_year=1949, author_id=1, rating=5),
            Book(title="Animal Farm", isbn="9780451526342", publication_year=1945, author_id=1, rating=4),
            Book(title="To Kill a Mockingbird", isbn="9780061120084", publication_year=1960, author_id=2, rating=5),
            Book(title="The Great Gatsby", isbn="9780743273565", publication_year=1925, author_id=3, rating=4),
            Book(title="Pride and Prejudice", isbn="9781503290563", publication_year=1813, author_id=4, rating=5)
        ]

        db.session.bulk_save_objects(books)
        db.session.commit()
        print("Added 5 sample books with authors!")

    with app.app_context():
        # Check if books already exist
        if Book.query.count() > 0:
            print("Books already exist in database")
            return

        # Create authors dictionary with complete details
        authors = {
            "George Orwell": {
                "birth_date": date(1903, 6, 25),
                "death_date": date(1950, 1, 21),
                "nationality": "British"
            },
            "Harper Lee": {
                "birth_date": date(1926, 4, 28),
                "death_date": date(2016, 2, 19),
                "nationality": "American"
            },
            "F. Scott Fitzgerald": {
                "birth_date": date(1896, 9, 24),
                "death_date": date(1940, 12, 21),
                "nationality": "American"
            },
            "Jane Austen": {
                "birth_date": date(1775, 12, 16),
                "death_date": date(1817, 7, 18),
                "nationality": "British"
            }
        }

        # Create authors if they don't exist
        created_authors = {}
        for name, details in authors.items():
            author = Author.query.filter_by(name=name).first()
            if not author:
                author = Author(
                    name=name,
                    birth_date=details["birth_date"],
                    date_of_death=details["death_date"],
                    nationality=details["nationality"]
                )
                db.session.add(author)
                db.session.commit()
            created_authors[name] = author.id

        # Sample books with complete data
        sample_books = [
            {
                "title": "1984",
                "isbn": "9780451524935",
                "year": 1949,
                "author": "George Orwell",
                "rating": 5
            },
            {
                "title": "Animal Farm",
                "isbn": "9780451526342",
                "year": 1945,
                "author": "George Orwell",
                "rating": 4
            },
            {
                "title": "To Kill a Mockingbird",
                "isbn": "9780061120084",
                "year": 1960,
                "author": "Harper Lee",
                "rating": 5
            },
            {
                "title": "The Great Gatsby",
                "isbn": "9780743273565",
                "year": 1925,
                "author": "F. Scott Fitzgerald",
                "rating": 4
            },
            {
                "title": "Pride and Prejudice",
                "isbn": "9781503290563",
                "year": 1813,
                "author": "Jane Austen",
                "rating": 5
            }
        ]

        # Add books to database
        for book in sample_books:
            if not Book.query.filter_by(isbn=book["isbn"]).first():
                new_book = Book(
                    title=book["title"],
                    isbn=book["isbn"],
                    publication_year=book["year"],
                    author_id=created_authors[book["author"]],
                    rating=book["rating"]
                )
                db.session.add(new_book)

        db.session.commit()
        print("Successfully added 5 sample books with authors!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)