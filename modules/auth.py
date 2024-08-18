from argon2 import PasswordHasher, exceptions
from modules.models import User, db
from flask_login import login_user

prefix = "prefixforbooks"
ph = PasswordHasher()

def login(email: str, password: str):
    try:
        current_password = prefix + password
        user = User.query.filter_by(email=email).first()
        if user and verify_password(user.password, current_password):
            login_user(user)
            return user
        return None
    except Exception as e:
        print("Error in login:", e)
        return None

def verify_password(db_password, current_password):
    try:
        return ph.verify(db_password, current_password)
    except exceptions.VerifyMismatchError:
        return False

def register(email: str, password: str, name: str):
    try:
        hashed_password = ph.hash(prefix + password)
        new_user = User(userName=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return new_user
    except Exception as e:
        print("Error:", str(e))
        db.session.rollback()
        return None
