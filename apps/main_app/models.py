from datetime import datetime
from flask_login import UserMixin
from apps.main_app.db import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    icon_path = db.Column(db.String(255), default='uploads/icons/default.png')
    banner_path = db.Column(db.String(255))
    bio = db.Column(db.Text)
    total_points = db.Column(db.Integer, default=0)

    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    shop_name = db.Column(db.String(200), nullable=False)
    crowd_level = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.String(100), nullable=False)
    helpful_count = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f"<Post {self.shop_name} by {self.user_name}>"