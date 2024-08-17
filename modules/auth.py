from argon2 import PasswordHasher, exceptions
from flask_sqlalchemy import SQLAlchemy
from modules.models import User, db
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

prefix:str = "prefixforbooks"
ph = PasswordHasher()

def login(email:str, password:str):
    try:
        currentPassword = prefix+password
        user = User.query.filter_by(email=email).first()
        verify = verifyPassword(user.password, currentPassword)
        if verify:
            login_user(user)
            return user
        else:
            return False
    except Exception as e:
        print("Error in login: ",e)
        return e

def verifyPassword (dbPassword, currentPassword):
    try:
        ph.verify(dbPassword, currentPassword)
        return True
    except exceptions.VerifyMismatchError:
        return False
    
def register(email:str, password:str, name:str):
    try:
        hashedPassword = ph.hash(prefix + password)
        new_user = User(userName=name, email = email, password=hashedPassword)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return new_user
    except Exception as e:
        print("Error: " + str(e))
        return None