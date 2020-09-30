from myproject import app,db
from flask import render_template, redirect, request, jsonify, url_for, flash, abort, request
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import uuid
from sqlalchemy.sql import func
from myproject.models import User, Comment, Review, Fight, FightCard
from myproject.forms import LoginForm, RegistrationForm, CommentForm, ReviewForm, FightForm
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/')
def home():
    return render_template('home.html', cards=FightCard.query.order_by(FightCard.id.desc()).all(),      #list of cards for main page
                                        maincard=FightCard.query.order_by(FightCard.id.desc()).first())     #grab most recent card for main image


@app.route('/fight_card/<int:card_id>')
def fight_card(card_id):
    card = FightCard.query.filter_by(id=card_id).first_or_404(card_id)
    return render_template('fight_card.html', fights=Fight.query.filter_by(fight_card=card.id).all(),       #filters fights by fight card
                                              card=card,
                                              reviews=Review.query.all())


@app.route('/fight_card/fight/<int:fight_id>', methods=('GET', 'POST'))
def fight(fight_id):
    reviewform = ReviewForm()
    commentform = CommentForm()
    fight = Fight.query.filter_by(id=fight_id).first_or_404(fight_id)
    fight_url = request.url
    rating = Review.query.with_entities(func.avg(Review.rating)).filter(Review.fight_id == fight.id).scalar()
    if reviewform.submitreview.data and reviewform.is_submitted():
        review = Review(rating=reviewform.rating.data,
                        title=reviewform.title.data,
                        content=reviewform.content.data,
                        user_id=current_user.username,
                        fight_id=fight.id)
        db.session.add(review)
        fight = Fight.query.filter_by(id=fight.id).first()
        fight.rating = Review.query.with_entities(func.avg(Review.rating)).filter(Review.fight_id == fight.id).scalar()
        db.session.commit()
        flash('Review has been posted')
        return redirect(url_for('fight', fight_id=fight_id))
    if commentform.submitcomment.data and commentform.validate():
        comment = Comment(content=commentform.content.data,
                          user_id=current_user.username,
                          review_id=request.form.get('reviewID'))
        db.session.add(comment)
        db.session.commit()
        flash('Comment has been posted')
        return redirect(url_for('fight', fight_id=fight_id))
    return render_template('fight.html', fights=Fight.query.filter_by(id=fight_id).all(),
                                         reviewform=reviewform,
                                         fight=fight,
                                         commentform=commentform,
                                         rating=rating,
                                         fight_url = fight_url,
                                         reviews=Review.query.filter_by(fight_id=fight.id),
                                         comments=Comment.query.all())


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user == None:
            flash('User does not exist!')
            return redirect(url_for('login'))
        if user.check_password(form.password.data) and user is not None:

            login_user(user)
            flash('Logged in successfully.')

            next = request.args.get('next')
            if next == None:
                next = url_for('home')

            return redirect(next)
        else:
            flash('Wrong password!')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email_exists = User.query.filter_by(email=form.email.data).first()
        if email_exists:
            flash('Email is already in use!')
            return redirect(url_for('register'))
        user_exists = User.query.filter_by(username=form.username.data).first()
        if user_exists:
            flash('Username is already in use!')
            return redirect(url_for('register'))
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out!')
    next = request.args.get('next')
    if next == None:
        next = url_for('home')
    return redirect(next)

application = app

if __name__ == '__main__':
    app.run()
