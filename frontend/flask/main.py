from flask import Flask, render_template, request
from core.result import Result
from core.user import User
import json

EMPTY_RESULT = Result(None, "")
CFG_FILE_PATHS = ["./configs/{}.json".format(x) for x in ['prod', 'test']]

app = Flask(__name__)
app.config.from_file(CFG_FILE_PATHS[app.config['DEBUG']],
                     load=json.load)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/users')
def users():
    return render_template("users.html", result=EMPTY_RESULT)


@app.route('/register', methods=['POST'])
def register():

    return render_template("users.html", EMPTY_RESULT)
    # usr = User(request.form.get('email'),
    #            request.form.get('mapshare_id'),
    #            request.form.get('mapshare_password'))
    # register_result = usr.register(conn)

    # if register_result.status:
    #     return render_template("index.html", result=register_result)
    # return render_template("new_user.html", result=register_result)


@app.route('/trips')
def trips():
    return render_template("trips.html")
