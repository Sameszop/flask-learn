from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from flask_migrate import Migrate
from modules.auth import register, login
from modules.models import Book, User, db, RegistrationForm, LoginForm, AddBookForm
from flask_login import login_required, current_user, login_user, logout_user, LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf, validate_csrf
from flask_talisman import Talisman
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv(".env")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')
loginManager = LoginManager(app)

talisman = Talisman(app, content_security_policy=None)  # Add CSP if needed
CORS(app)
csrf = CSRFProtect(app)
# Initialize the database and other extensions
db.init_app(app)
migrate = Migrate(app, db)

# User loader callback for Flask-Login
@loginManager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        print("Error:", e)
        return None

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if request.method == 'POST':
            if 'borrow' in request.form:
                return borrow()  # Handle borrowing logic if POST request

        books = Book.query.all()  # Retrieve all books
        csrf_token = generate_csrf()  # Generate CSRF token
        return render_template('index.html', books=books, user=current_user, csrf_token=csrf_token)
   
    except Exception as e:
        print("Error:", str(e))
        return "An error occurred", 500

@login_required
def borrow():
    try:
        # Validate CSRF token
        validate_csrf(request.form.get('csrf_token'))
        book_id = request.form['id']
        book = Book.query.get(int(book_id))
        if book and not book.owner_id:
            book.owner_id = current_user.id
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return "Book not found or already borrowed", 400
    except Exception as e:
        print("Exception:", str(e))
        db.session.rollback()
        return "An error occurred", 500

# Give back book route
@app.route('/giveBack', methods=['POST'])
@login_required
def giveBack():
    try:
        validate_csrf(request.form.get('csrf_token'))
        book_id = request.form.get('bookId')
        if not book_id or not book_id.isdigit():
            return "Invalid book ID", 400

        book = Book.query.get(int(book_id))
        if book is None:
            return "Book not found", 404

        book.owner_id = None
        db.session.commit()
        return redirect(url_for('home'))
    except Exception as e:
        print("Error:", str(e))
        db.session.rollback()
        return "An error occurred", 500

# Add book route
@app.route('/addBook', methods=['GET', 'POST'])
@login_required
def addBook():
    form = AddBookForm()

    if form.validate_on_submit():
        try:
            name = form.name.data
            release = form.release.data
            picture = form.picture.data
            new_book = Book(name=name, release=release, picture=picture)
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            print("Exception:", str(e))
            db.session.rollback()
            return "An error occurred", 500

    return render_template("addBook.html", form=form)
# userpassword = h5q8e21J89587i0U  email= lord@pretty.flacko

# My books route
@app.route('/myBooks')
@login_required
def myBooks():
    try:
        csrf_token = generate_csrf()  # Generate CSRF token
        books = Book.query.filter_by(owner_id=current_user.id).all()
        return render_template("myBooks.html", books=books, user=current_user, csrf_token=csrf_token)
    except Exception as e:
        print("Error:", str(e))
        return "An error occurred", 500

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def reg():
    try:
        # Check if the user is already logged in
        if current_user.is_authenticated:
            return redirect(url_for('home'))

        form = RegistrationForm()
        
        if form.validate_on_submit():
            password = form.password.data
            re_password = form.re_password.data
            
            if password == re_password:
                user = register(form.email.data, password, form.name.data)
                if user:
                    login_user(user)
                    return redirect(url_for('home'))
                else:
                    return "Registration failed", 400
            else:
                return "Passwords do not match", 400

        return render_template('auth.html', form=form)

    except Exception as e:
        print("Error:", str(e))
        return "An error occurred", 500
# Login route
@app.route('/login', methods=['GET', 'POST'])
def log():
    try:
        # Redirect authenticated users away from the login page
        if current_user.is_authenticated:
            return redirect(url_for('home'))

        form = LoginForm()

        if form.validate_on_submit():  # This will also validate the CSRF token
            user = login(form.email.data, form.password.data)
            if user:
                login_user(user)
                return redirect(url_for('home'))
            else:
                return "Login failed", 400

        return render_template('auth.html', form=form)

    except Exception as e:
        print("Error:", str(e))
        return "An error occurred", 500

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
