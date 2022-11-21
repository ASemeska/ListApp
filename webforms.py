from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea

class NamerForm(FlaskForm):
    name = StringField("Whats your name", validators=[DataRequired()])
    submit = SubmitField("Submit name")

class PasswordForm(FlaskForm):
	email = StringField("Whats your email", validators=[DataRequired()])
	password_hash = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField("Submit name")

class UserForm(FlaskForm):
	name = StringField("Whats your name", validators=[DataRequired()])
	email = StringField("Whats your email", validators=[DataRequired()])
	username = StringField("Whats your username", validators=[DataRequired()])
	submit = SubmitField("Submit name")
	password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])


class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	author = StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")