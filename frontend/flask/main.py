from flask import Flask, render_template, request
from core.result import Result
from core.user import User
from core.db import init_app as db_init_app, get_conn
import json

EMPTY_RESULT = Result(None, "")
CFG_FILE_PATHS = ["./configs/{}.json".format(x) for x in ['prod', 'test']]

app = Flask(__name__)
app.config.from_file(CFG_FILE_PATHS[app.config['DEBUG']],
                     load=json.load)

db_init_app(app)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/users')
def users():
    return render_template("users.html", result=EMPTY_RESULT)


@app.route('/change_mapshare_pw', methods=['POST'])
def change_mapshare_pw():
    return render_template("users.html", result=EMPTY_RESULT)


@app.route('/register', methods=['POST'])
def register():

    get_conn()

    usr = User(request.form.get('mapshare_id'),
               request.form.get('mapshare_password'))
    register_result = usr.register(debug=app.config['DEBUG'])
    return render_template("users.html", result=register_result)


@app.route('/trips')
def trips():
    return render_template("trips.html", result=EMPTY_RESULT)


@app.route('/user_trips', methods=['POST'])
def user_trips():

    get_conn()

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    # usr = User(current_mapshare_id)

    # get trip form data (if applicable)

    # get all user trips (might be empty)

    return render_template("user_trips.html",
                           current_mapshare_id=current_mapshare_id,
                           user_result=EMPTY_RESULT,
                           trip_result=EMPTY_RESULT)


@app.route('/add_trip', methods=['POST'])
def add_trip():
    return render_template("trips.html", result=EMPTY_RESULT)


@app.route('/alter_trip', methods=['POST'])
def alter_trip():
    return render_template("trips.html", result=EMPTY_RESULT)


@app.route('/delete_trip', methods=['POST'])
def delete_trip():
    return render_template("trips.html", result=EMPTY_RESULT)
