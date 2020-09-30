from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField, validators, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'pass_confirm', message='Passwords Must Match!')])
    pass_confirm = PasswordField(
        'Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register!')

    def check_email(self, field):
        # Check if not None for that user email!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been registered already!')

    def check_username(self, field):
        # Check if not None for that username!
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Sorry, that username is taken!')


class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submitcomment = SubmitField('Submit')
    review_id = HiddenField('ReviewID')


class ReviewForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    rating = RadioField('Rating', choices=[(
        10), (9), (8), (7), (6), (5), (4), (3), (2), (1)], coerce=int, validators=[DataRequired()])
    submitreview = SubmitField('Submit')


class FightForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    fight_image = StringField('Image')
    submit = SubmitField('Submit')
