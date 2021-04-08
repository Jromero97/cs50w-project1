import requests
from flask import render_template, redirect, flash, jsonify, session, request
from werkzeug.security import check_password_hash, generate_password_hash
from src import app, db
from src.decorators import sign_in_required


@app.route('/')
@app.route('/index')
@sign_in_required
def index():
    return render_template('index.html', title='Home', user=session.get('username'))


@app.route('/book/<isbn>', methods=['GET', 'POST'])
@sign_in_required
def book(isbn):
    if request.method == 'POST':
        current_user = session['user_id']

        rating = request.form.get('rating')
        comment = request.form.get('comment')

        book_query = db.execute('SELECT book_id FROM books where isbn = :isbn', {
            'isbn': isbn
        })

        book_data = book_query.fetchone()
        book = book_data[0]

        review_query = db.execute('SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id', {
            'user_id': current_user,
            'book_id': book
        })

        if review_query.rowcount == 1:
            flash('You reviewed this book before', 'warning')
            return redirect('/book/' + isbn)

        rating = int(rating)

        db.execute(
            'INSERT INTO reviews (user_id, book_id, comment, rating) VALUES (:user_id, :book_id, :comment, :rating)',
            {
                'user_id': current_user,
                'book_id': book,
                'comment': comment,
                'rating': rating
            }
        )

        db.commit()

        flash('Review submitted successful', 'success')
        return redirect('/book/' + isbn)
    else:

        books_query = db.execute(
            'SELECT isbn, title, author, year FROM books WHERE isbn = :isbn',
            {
                'isbn': isbn
            }
        )

        books_info = books_query.fetchall()

        book_id_query = db.execute(
            'SELECT book_id from books WHERE isbn = :isbn',
            {
                'isbn': isbn
            }
        )

        book_data = book_id_query.fetchone()
        book = book_data[0]


        reviews_query = db.execute(
            """SELECT users.username, comment, rating, published_time as time FROM users
            INNER JOIN reviews ON users.user_id = reviews.user_id where book_id = :book ORDER BY time""",
            {
                'book': book
            }
        )

        reviews = reviews_query.fetchall()

        return render_template('book.html', title=books_info[0]['title'], book=books_info, reviews=reviews)


@app.route('/api/<isbn>', methods=['GET'])
@sign_in_required
def book_summary(isbn):
    query = db.execute(
        """
        SELECT title, author, year, isbn, COUNT(reviews.review_id) as review_count, AVG(reviews.rating) as average_score 
        FROM books INNER JOIN reviews ON books.book_id = reviews.book_id
        WHERE isbn = :isbn GROUP BY title, author, year, isbn
        """,
        {
            'isbn': isbn
        }
    )

    if query.rowcount != 1:
        return jsonify({'error': 'Invalid ISBN'}), 422

    temp_book = query.fetchone()

    summary = dict(temp_book)

    summary['average_score'] = float('%2.f' % (summary['average_score']))

    return jsonify(summary)


@app.route('/signin', methods=['GET', 'POST'])
def signin():

    session.clear()

    username = request.form.get('username')
    password = request.form.get('password')

    print(username, password)

    if request.method == 'POST':

        if not username:
            return render_template('error.html', message='Username required', code=400)

        if not password:
            return render_template('error.html', message='Password required', code=400)

        query = db.execute(
            """
            SELECT * FROM users WHERE username = :username
            """,
            {
                'username': username
            }
        )

        print(query)

        user = query.fetchone()

        print(user)

        if user is None or not check_password_hash(user[2], password):
            return render_template('error.html', message='Invalid password or username', code=400)

        session['user_id'] = user[0]
        session['username'] = user[1]

        return redirect('/')
    else:
        return render_template('signin.html', title='Sign In')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    session.clear()

    if request.method == 'POST':
        if not request.form.get('username'):
            return render_template('error.html', message='Username required', code=400)

        if not request.form.get('password'):
            return render_template('error.html', message='Password required', code=400)

        if not request.form.get('email'):
            return render_template('error.html', message='Email required', code=400)

        check_user_query = db.execute(
            """
            SELECT * FROM users WHERE username = :username
            """,
            {
                'username': request.form.get('username')
            }
        )

        if check_user_query.rowcount != 0:
            return render_template('error.html', message='This username has been taken, try another one', code=400)

        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        db.execute(
            """
            INSERT INTO users (username, password, email) VALUES (:username, :password, :email)
            """,
            {
                'username': username,
                'password': hash,
                'email': email
            }
        )

        db.commit()

        flash("You've create your account successfully", 'success')

        return redirect('/signin')
    else:
        return render_template('singup.html', title='Sign Up')


@app.route('/search', methods=['GET'])
@sign_in_required
def search():
    book = request.args.get('book')

    if not book:
        return render_template('error.html', message="You must insert a book", code=400)

    query = "%" + book + "%"

    query = query.title()

    rows = db.execute(
        """
        SELECT isbn, title, author, year FROM books WHERE isbn like :query OR author LIKE :query OR title 
        LIKE :query LIMIT 20
        """, {
            'query': query
        })

    if rows.rowcount == 0:
        return render_template('error.html', message="We can't find books with that parameter", code=422)

    books = rows.fetchall()

    return render_template('index.html', title='Results', user=session.get('username'), books=books)
