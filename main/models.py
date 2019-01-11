from main import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return UsersTable.query.get(int(user_id))


class UsersTable(db.Model, UserMixin):
    '''This is a class that creates the register database table'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('PostsTable', backref='author', lazy=True)

    def __repr__(self):
        return f'User({self.username}, {self.email}, {self.image_file})'


class PostsTable(db.Model):
    '''This is the class that creates the posts table'''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), nullable=False)

    def __repr__(self):
        return f'Post({self.title},{self.date_posted})'
