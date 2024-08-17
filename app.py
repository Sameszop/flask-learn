from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from flask_migrate import Migrate
from modules.auth import register, login
from modules.models import Book, User, db
from flask_login import login_required, current_user, LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
talisman = Talisman(app, content_security_policy=None)
CORS(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SESSION_COOKIE_SECURE'] = True
app.secret_key = os.getenv('SECRET_KEY')
user=None
db.init_app(app)  
login_manager = LoginManager(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['POST', 'GET'])
def home():
    # if 'user_id' in session and not current_user:
    #     user = User.query.get(session['user_id'])
    #     if user:
    #         login_user(user)  # Log the user in if they are not already authenticated

    if request.method == 'POST':
        borrow()    

    books = Book.query.all()
    return render_template('index.html', books=books, user=user)

@login_required
def borrow():
    try:
        user = current_user
        book_id = request.form['id']  # Access form data
        book = Book.query.filter_by(id=book_id).first()  # Get the first matching book
        if book and user and not book.owner_id:  # Ensure book is found and is not borrowed
            book.owner_id = user.id
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return "Book not found, already borrowed, or no user", 400  # Return a client error
    except Exception as e:
        print("Exception: ", e)
        db.session.rollback()  # Rollback the session on error
        return "An error occurred", 500  # Return a server error

@app.route('/giveBack', methods=['POST'])
def giveBack():
    try:
        bookID = request.form.get('bookId')
        if not bookID or not bookID.isdigit():
            return "Invalid book ID", 400  # Return a bad request error
        book = Book.query.filter_by(id=int(bookID)).first()
        if book is None:
            return "Book not found", 404  # Return a not found error
        book.owner_id = None
        db.session.commit()
        return redirect(url_for('home')) 
    except Exception as e:
        print("Error:", str(e))  # Convert the exception to a string
        return "An error occurred", 500  # Return a server error

@app.route('/addBook', methods=['GET', 'POST'])
def addBook():
    if request.method == 'POST':
        try:
            name = request.form['name']
            release = datetime.strptime(request.form['release'], '%Y-%m-%d')
            picture = request.form['picture']
            new_book = Book(name=name, release=release, picture=picture)
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('home', book_id=new_book.id))  # Redirect to the book detail page
        except Exception as e:
            print("Exception: ", e)
            db.session.rollback()  # Rollback the session on error
            return redirect(url_for('addBook'))  # Redirect back to the form on error
    return render_template("addBook.html")

@app.route('/myBooks')
@login_required
def myBooks():
    if current_user:
        books = Book.query.all()
        return render_template("myBooks.html", books=books, user=user)
    else:
        return redirect(url_for('reg'))  # Redirect back to the form on error
     

@app.route('/register', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        password = request.form['password']
        re_password = request.form['re-password']

        if password == re_password:
            user = register(request.form['email'], password, request.form['name'])
            if user:
                session['user_id'] = user.id  # Store user ID in session
                return redirect(url_for('home'))
            else:
                return "Registration failed", 400
        else:
            return "Passwords do not match", 400
    return render_template('auth.html')

@app.route('/login', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        user = login(request.form['email'], request.form['password'])
        if user:
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('home'))
        else:
            return "Login failed", 400
    return render_template('auth.html')

# Initialize database tables (optional if you're using Flask-Migrate)
# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(debug=True)