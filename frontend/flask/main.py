from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/users')
def users():
    return render_template("users.html")


@app.route('/trips')
def trips():
    return render_template("trips.html")
