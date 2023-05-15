import os
import sys
import psycopg2
import configparser
from flask import Flask, render_template, request, g
sys.path.insert(0, os.path.abspath("./flaskr"))

from helpers.user import User
from helpers.result import Result
# from helpers.trip import Trip

config = configparser.ConfigParser()
config.read('./fireside.cfg')

g.conn = psycopg2.connect(
    database=config['DB']['DB_NAME'],
    user=config['DB']['DB_USER'],
    password=config['DB']['DB_PASSWORD'],
    host=config['DB']['DB_HOST'],
    port=config['DB']['DB_PORT'],
)

# Create app

# app = Flask(__name__)
# app.config['DEBUG'] = True


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/new_user')
    def new_user():
        empty_result = Result(None, "")
        return render_template("new_user.html", result=empty_result)

    @app.route('/new_user', methods=['POST'])
    def register():
        usr = User(request.form.get('email'),
                   request.form.get('mapshare_id'),
                   request.form.get('mapshare_password'))
        registration_result = usr.register(g.conn)
        return render_template("new_user.html", result=registration_result)

    return app
