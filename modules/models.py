from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(50), nullable=False)
    books = db.relationship('Book', backref='user', lazy=True)
    password = db.Column(db.String(255), nullable=False)  # Increase to 255
    email = db.Column(db.String, nullable=False)
    created = db.Column(db.Date, default=date.today)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    release = db.Column(db.Date)
    picture = db.Column(db.String, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)