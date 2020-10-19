from myproject import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    comments = db.relationship('Comment', backref='author', lazy=True)

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return f"User('{self.email}', '{self.username}')"

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.username'))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'))

    def __init__(self, content, user_id, review_id):
        self.content = content
        self.user_id = user_id
        self.review_id = review_id

    def __repr__(self):
        return f"Comment('{self.user_id}','{self.content}')"


class Review(db.Model):

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text(300))
    fight_id = db.Column(db.Integer, db.ForeignKey('fights.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.username'))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    rating = db.Column(db.Integer)
    comments = db.relationship("Comment", backref="reviews", lazy='dynamic')


class Fight(db.Model):

    __tablename__ = 'fights'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    fighter_1 = db.Column(db.String(50))
    fighter_2 = db.Column(db.String(50))
    winner = db.Column(db.String(50))
    method = db.Column(db.String(25))
    round = db.Column(db.Integer)
    time = db.Column(db.String(10))
    rating = db.Column(db.Float)
    fight_image = db.Column(db.String(100))
    fight_card = db.Column(db.String(15), db.ForeignKey('fightcards.id'))
    path = db.Column(db.String(100))


class FightCard(db.Model):
    __tablename__ = 'fightcards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    card_image = db.Column(db.String(100))
    avg_rating = db.Column(db.Float)
    description = db.Column(db.Text(300))
