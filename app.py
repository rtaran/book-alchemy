# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import db, Author, Book
import os

app = Flask(__name__, instance_path=os.path.abspath("data"))
app.secret_key = 'your-secret-key-here'  # Needed for flash messages
os.makedirs(app.instance_path, exist_ok=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "library.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Add Author Route
@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        try:
            new_author = Author(
                name=request.form['name'],
                birth_date=request.form['birth_date'],
                nationality=request.form['nationality']
            )
            db.session.add(new_author)
            db.session.commit()
            flash('Author added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding author: {str(e)}', 'error')
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


# Add Book Route
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()

    if request.method == 'POST':
        try:
            new_book = Book(
                title=request.form['title'],
                publication_date=request.form['publication_date'],
                isbn=request.form['isbn'],
                author_id=request.form['author_id']
            )
            db.session.add(new_book)
            db.session.commit()
            flash('Book added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding book: {str(e)}', 'error')
        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


# Home Route with Sorting
@app.route('/')
def home():
    sort_by = request.args.get('sort', 'title')

    if sort_by == 'author':
        books = Book.query.join(Author).order_by(Author.name).all()
    else:
        books = Book.query.order_by(Book.title).all()

    return render_template('home.html', books=books, sort_by=sort_by)


if __name__ == '__main__':
    app.run(debug=True)