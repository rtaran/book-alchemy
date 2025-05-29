import requests
import os  # Still needed for os.getenv and os.makedirs
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from data_models import db, Author, Book
from sqlalchemy import or_
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, date
from flask_migrate import Migrate

load_dotenv()

# Configure absolute path
basedir = Path(__file__).parent.absolute()
database_path = basedir / 'data' / 'library.sqlite'

# Create data directory if it doesn't exist
if not (database_path.parent).exists():
    database_path.parent.mkdir(parents=True)

app = Flask(__name__)
# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key_for_development')

db.init_app(app)
migrate = Migrate(app, db)


# Routes
@app.route('/')
def home():
    """
    Display the home page with a list of books, optionally filtered by search term.

    Returns:
        Rendered home template with books and search parameters
    """
    search_term = request.args.get('q', '')
    sort_by = request.args.get('sort', 'title')

    query = Book.query.join(Author)

    if search_term:
        query = query.filter(or_(
            Book.title.ilike(f'%{search_term}%'),
            Author.name.ilike(f'%{search_term}%')
        ))

    books = query.order_by(
        Author.name if sort_by == 'author' else Book.title
    ).all()

    return render_template(
        'home.html', 
        books=books, 
        search_term=search_term, 
        sort_by=sort_by
    )

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Display the add author form and handle form submission.

    Returns:
        Rendered add_author template or redirect to add_author route
    """
    if request.method == 'POST':
        try:
            # Check if author already exists
            author_name = request.form['name']
            existing_author = Author.query.filter_by(name=author_name).first()
            if existing_author:
                flash(f'Author "{author_name}" already exists in the database!', 'warning')
                return redirect(url_for('add_author'))

            # Convert date strings to Python date objects
            birth_date = None
            if request.form['birth_date']:
                birth_date = datetime.strptime(
                    request.form['birth_date'], '%Y-%m-%d'
                ).date()

            date_of_death = None
            if request.form.get('date_of_death'):
                date_of_death = datetime.strptime(
                    request.form['date_of_death'], '%Y-%m-%d'
                ).date()

            author = Author(
                name=author_name,
                birth_date=birth_date,
                date_of_death=date_of_death,
                nationality=request.form.get('nationality', None)
            )

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
    """
    Display the add book form and handle form submission.

    Returns:
        Rendered add_book template or redirect to add_book route
    """
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
            flash('Error: This ISBN already exists in the database!', 'warning')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding book: {str(e)}', 'warning')

    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """
    Display details for a specific book.

    Args:
        book_id: The ID of the book to display

    Returns:
        Rendered book_detail template with the book object
    """
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)


@app.route('/author/<int:author_id>/delete', methods=['GET', 'POST'])
def delete_author(author_id):
    """
    Delete an author and redirect to delete their books if they have any.

    Args:
        author_id: The ID of the author to delete

    Returns:
        A redirect to either delete_book or home
    """
    # Find the first book by this author and redirect to delete_book
    book = Book.query.filter_by(author_id=author_id).first()
    if book:
        return redirect(url_for('delete_book', book_id=book.id))

    # If no books found, just delete the author
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash(f'Author {author.name} deleted!', 'success')
    return redirect(url_for('home'))


@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
def delete_book(book_id):
    """
    Delete a book and optionally its author if it's the author's only book.

    Args:
        book_id: The ID of the book to delete

    Returns:
        A redirect to the home page
    """
    book = Book.query.get_or_404(book_id)
    book_title = book.title

    # Check if this is the author's only book
    author = book.author
    author_books_count = Book.query.filter_by(author_id=author.id).count()

    db.session.delete(book)

    # If this was the author's only book, delete the author too
    if author_books_count == 1:
        db.session.delete(author)
        flash(f'Book "{book_title}" and author {author.name} deleted!', 'success')
        db.session.commit()
        return redirect(url_for('home'))

    flash(f'Book "{book_title}" deleted!', 'success')
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/recommend')
def recommend_books():
    """
    Generate book recommendations based on the user's existing books.

    Uses an external AI API to generate personalized book recommendations
    based on the books in the database and their ratings.

    Returns:
        Rendered recommendations template with AI-generated recommendation
    """
    books = Book.query.all()

    if not books:
        recommendation = None
    else:
        # Build a nice input prompt for the AI
        book_list = "\n".join([
            f"{book.title} by {book.author.name} (Rating: {book.rating})" 
            for book in books
        ])
        prompt = (
            f"Based on the following books and their ratings, "
            f"suggest a new book I might enjoy:\n\n{book_list}"
        )

        # RapidAPI ChatGPT API setup
        url = "https://chatgpt-42.p.rapidapi.com/chat"
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "model": "gpt-4o-mini"
        }
        headers = {
            "x-rapidapi-key": os.getenv('RAPIDAPI_KEY'),  # <-- your real key
            "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            recommendation = result['choices'][0]['message']['content']
        except Exception as e:
            recommendation = f"Error generating recommendation: {str(e)}"

    return render_template('recommendations.html', recommendation=recommendation)


def add_sample_books():
    """
    Add sample books and authors to the database for testing purposes.

    This function checks if books already exist in the database and adds
    sample data only if the database is empty.
    """
    with app.app_context():
        # Check if books already exist
        if Book.query.count() > 0:
            print("Books already exist in database")
            return

        # Create authors
        authors = [
            Author(
                name="George Orwell", 
                birth_date=date(1903, 6, 25), 
                date_of_death=date(1950, 1, 21),
                nationality="British"
            ),
            Author(
                name="Harper Lee", 
                birth_date=date(1926, 4, 28), 
                date_of_death=date(2016, 2, 19),
                nationality="American"
            ),
            Author(
                name="F. Scott Fitzgerald", 
                birth_date=date(1896, 9, 24), 
                date_of_death=date(1940, 12, 21),
                nationality="American"
            ),
            Author(
                name="Jane Austen", 
                birth_date=date(1775, 12, 16), 
                date_of_death=date(1817, 7, 18),
                nationality="British"
            )
        ]

        db.session.bulk_save_objects(authors)
        db.session.commit()

        # Create books
        books = [
            Book(
                title="1984", 
                isbn="9780451524935", 
                publication_year=1949, 
                author_id=1, 
                rating=5
            ),
            Book(
                title="Animal Farm", 
                isbn="9780451526342", 
                publication_year=1945, 
                author_id=1, 
                rating=4
            ),
            Book(
                title="To Kill a Mockingbird", 
                isbn="9780061120084", 
                publication_year=1960, 
                author_id=2, 
                rating=5
            ),
            Book(
                title="The Great Gatsby", 
                isbn="9780743273565", 
                publication_year=1925, 
                author_id=3, 
                rating=4
            ),
            Book(
                title="Pride and Prejudice", 
                isbn="9781503290563", 
                publication_year=1813, 
                author_id=4, 
                rating=5
            )
        ]

        db.session.bulk_save_objects(books)
        db.session.commit()
        print("Added 5 sample books with authors!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
