import os
from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SECRET_KEY'] = 'AS#$54744#@#SDFadqwef'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))
############Model############

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), nullable=False, unique=True)
	name = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	favourite_color = db.Column(db.String(120))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	password_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError('password is not readable attribute')
	
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<Name %r>' % self.name

class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	author = db.Column(db.String(255))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))

############Forms############
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
############ROUTES############

@app.route('/')
def index():

    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# Check the hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login Succesfull!!")
				return redirect(url_for('posts'))
			else:
				flash("Wrong Password - Try Again!")
		else:
			flash("That User Doesn't Exist! Try Again...")

	return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You have been log out!")
	return redirect(url_for('login'))

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name = name)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(name=form.name.data, email=form.email.data,  username= form.username.data, password_hash = hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.email.data = ''
		form.username = ''	
		form.password_hash.data = ''	
		flash("User Added Successfully!")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", 
		form=form,
		name=name,
		our_users=our_users)

@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts = posts)

@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Posts(title = form.title.data, content = form.content.data, author = form.author.data, slug = form.slug.data)
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''

		db.session.add(post)
		db.session.commit()
		flash("Post submitted successfully!")

	return render_template("add_post.html", form = form)

@app.route('/posts/<int:id>', methods=['GET', 'POST'])
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template("post.html", post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		post.author = form.author.data
		post.slug = form.slug.data
		db.session.add(post)
		db.session.commit()
		flash("Post updated sucessfully!")
		return redirect(url_for('post', id = post.id))
	form.title.data = post.title
	form.content.data = post.content
	form.author.data = post.author
	form.slug.data = post.slug
	return render_template('edit_post.html', form = form)


# Update entry
@app.route('/update/<int:id>', methods =['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if form.validate_on_submit():
		db.session.delete(name_to_update)
		db.session.commit()
		name_to_update = Users(id= name_to_update.id, name=form.name.data, email=form.email.data, favourite_color = form.favourite_color.data, date_added=name_to_update.date_added)
		if name_to_update:
			db.session.add(name_to_update)
			db.session.commit()
			flash("User Updated Sucessfully!")
			return render_template("update.html", form=form, name_to_update= name_to_update)
		else:
			flash("Something went wrong, please try again!")
			return render_template("update.html", form=form, name_to_update= name_to_update)
	else:
			return render_template("update.html", form=form, name_to_update= name_to_update, id=id)

@app.route('/posts/delete/<int:id>', methods=['GET', 'POST'])
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	try:
		db.session.delete(post_to_delete)
		db.session.commit()
		flash("Post deleted Sucessfully!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)
	except:
		flash("Post was not deleted, try again!")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts = posts)



@app.route('/delete/<int:id>')
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()
	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User Deleted Successfully!")
		our_users = Users.query.order_by(Users.date_added)
		return render_template("add_user.html", form=form, name=name, our_users=our_users)

	except:
			flash("There was an problem deleting User")
			return render_template("add_user.html", form=form, name=name, our_users=our_users)

@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	pasword = None
	pw_to_check = None
	passed = None
	form = PasswordForm()
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		form.email.data = ''
		form.password_hash.data = ''
		pw_to_check = Users.query.filter_by(email=email).first()
		passed = check_password_hash(pw_to_check.password_hash, password)
	return render_template("test_pw.html", email = email,
		pasword = pasword,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)



@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully!")

	return render_template("name.html", 
		name = name,
		form = form)
############CUSTOM ERRORS############ 

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)