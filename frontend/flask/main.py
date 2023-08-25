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
    print(app.config)
    return render_template("index.html")


@app.route('/users')
def users():
    return render_template("users.html", result=EMPTY_RESULT)


@app.route('/change_mapshare_pw', methods=['POST'])
def change_mapshare_pw():
    return render_template("users.html", result=EMPTY_RESULT)


@app.route('/register', methods=['POST'])
def register():

    conn = get_conn()

    usr = User(request.form.get('mapshare_id'),
               request.form.get('mapshare_password'))
    register_result = usr.register(conn, debug=app.config['DEBUG'])

    if register_result.status:
        return render_template("users.html", result=register_result)
    return render_template("users.html", result=register_result)


@app.route('/trips')
def trips():
    return render_template("trips.html", result=EMPTY_RESULT)


@app.route('/add_trip', methods=['POST'])
def add_trip():
    return render_template("trips.html", result=EMPTY_RESULT)
