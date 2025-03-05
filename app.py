from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import db, Author, Book
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key-here'  # Needed for flash messages

db.init_app(app)


@app.route('/')
def home():
    search_term = request.args.get('q', '')
    sort_by = request.args.get('sort', 'title')

    # Base query
    query = Book.query.join(Author)

    # Apply search filter
    if search_term:
        query = query.filter(or_(
            Book.title.ilike(f'%{search_term}%'),
            Author.name.ilike(f'%{search_term}%')
        ))

    # Apply sorting
    if sort_by == 'author':
        books = query.order_by(Author.name).all()
    else:
        books = query.order_by(Book.title).all()

    return render_template('home.html',
                         books=books,
                         search_term=search_term)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date'] or None
        date_of_death = request.form['date_of_death'] or None

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        flash('Author added successfully!', 'success')
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)