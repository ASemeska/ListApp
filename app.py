import os
from flask import Flask, render_template

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

############ROUTES############

@app.route('/')
def home():
    return "<h1>Hello World!</h1>"


@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name = name)

############CUSTOM ERRORS############ 

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)