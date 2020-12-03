from myproject import app, db, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL, client, facebook, OAuthException
from flask import render_template, redirect, request, jsonify, url_for, flash, abort, request, session
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import uuid
import requests
import json
from sqlalchemy.sql import func
from myproject.models import User, Comment, Review, Fight, FightCard
from myproject.forms import LoginForm, RegistrationForm, CommentForm, ReviewForm, FightForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.consumer import oauth_authorized, oauth_error

@app.route('/')
def home():
    return render_template('home.html', cards=FightCard.query.order_by(FightCard.id.desc()).all(),      #list of cards for main page
                                        maincard=FightCard.query.order_by(FightCard.id.desc()).first())     #grab most recent card for main image
@app.route('/fuckoff')
def fuckoff():
    pass

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
        review_exists = Review.query.filter_by(user_id=current_user.username, fight_id=fight.id).first()
        if review_exists:
            flash("You've already left a review for this fight!")
            return redirect(url_for('fight', fight_id=fight_id))
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

            login_user(user, remember=True)
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
        login_user(user, remember=True)
        flash('Thanks for registering!')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/google_login")
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(authorization_endpoint,
                                             redirect_uri=request.base_url + "/callback",
                                             scope=["openid", "email", "profile"])
    return redirect(request_uri)
# create/login local user on successful OAuth login
@app.route("/google_login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(token_endpoint,
                                                            authorization_response=request.url,
                                                            redirect_url=request.base_url,
                                                            code=code)
    token_response = requests.post(token_url,
                                   headers=headers,
                                   data=body,
                                   auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET))
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["name"]
    else:
        return "User email not available or not verified by Google.", 400
    user = User.query.filter_by(email=users_email).first()
    if user:
        login_user(user, remember=True)
    else:
        user = User(email=users_email,
                    username=users_name,
                    password=unique_id)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
    flash('You are logged in with Google!')
    next = request.args.get('next')
    if next == None:
        next = url_for('home')
    return redirect(next)

@app.route('/facebook_login')
def facebook_login():
    callback = url_for('facebook_authorized',
                        _external=True)
    return facebook.authorize(callback=callback)

@app.route('/facebook_login/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me?fields=id,name,email')
    user = User.query.filter_by(email=me.data['email']).first()
    if user:
        login_user(user, remember=True)
    else:
        user = User(email=me.data['email'],
                    username=me.data['name'],
                    password="facebook")
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
    flash('You are logged in with Facebook!')
    next = request.args.get('next')
    if next == None:
        next = url_for('home')
    return redirect(next)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

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
