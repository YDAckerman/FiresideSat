import os
import sys
sys.path.insert(0, os.path.abspath("./flaskr"))

from flask import Flask, render_template, request
# from flask_sqlalchemy import SQLAlchemy
from helpers.db import get_conn
from helpers.transactions import add_new_user


# Create app

# app = Flask(__name__)
# app.config['DEBUG'] = True


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

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

    # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Hello, World!'

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/new_user')
    def new_user():
        result = {'none': ""}
        return render_template("new_user.html", result=result)

    @app.route('/register', methods=['POST'])
    def register():
        # email = request.form.get('email')
        # mapshare_id = request.form.get('mapshare_id')
        # mapshare_password = request.form.get('mapshare_password')
        # conn = get_conn()
        # result = add_new_user(conn, email, mapshare_id, mapshare_password)
        result = {"success": "You have been registered."}

        return render_template("new_user.html", result=result)

    return app
