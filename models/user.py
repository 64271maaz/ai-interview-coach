from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Is user ke saare interview attempts (ek user, kai interviews)
    interviews = db.relationship('Interview', backref='user', lazy=True)

    def set_password(self, password):
        """Password ko hash karke save karta hai, plain text kabhi nahi"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Login ke waqt password verify karta hai"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'