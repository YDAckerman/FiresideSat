from flask import Flask, render_template, request
from core.result import Result
from core.user import User
from core.trip import Trip
from core.db import init_app as db_init_app, get_conn, db_submit
from core.sql_queries import SqlQueries

import json
import requests

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


@app.route('/set_aqi_key', methods=['POST'])
def set_aqi_key():

    aqi_result = EMPTY_RESULT
    airnow_key = request.form.get('airnow_key')

    # test the given key
    test_endpoint = 'https://www.airnowapi.org/' \
        + 'aq/observation/zipCode/current/' \
        + '?format=application/json' \
        + '&zipCode=94703' \
        + f'&API_KEY={airnow_key}'
    resp_status = requests.get(test_endpoint).status_code

    if resp_status == 200:
        # if it works, send it to the database
        get_conn()
        qrys = SqlQueries()
        aqi_result = db_submit(qrys.upsert_airnow_key,
                               {'airnow_key': airnow_key},
                               Result(True, "Key set successfully"))

    else:
        # otherwise return an error result
        aqi_result = Result(False, 'API Key did not work (status:'
                            + f' {resp_status})')

    return render_template("users.html", result=aqi_result)


@app.route('/trips')
def trips():
    return render_template("trips.html", result=EMPTY_RESULT)


@app.route('/user_trips', methods=['POST'])
def user_trips():

    get_conn()
    user_result = EMPTY_RESULT
    trip_result = EMPTY_RESULT
    user_trips = []

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)

    if not usr.exists:
        user_result = Result(None, "User does not exist")

    else:
        if len(usr.trips) == 0:
            trip_result = Result(None, "There are no trips to display")
        else:
            user_trips = usr.trips

    return render_template("user_trips.html",
                           current_mapshare_id=current_mapshare_id,
                           user_result=user_result,
                           trip_result=trip_result,
                           user_trips=user_trips)


@app.route('/add_trip', methods=['POST'])
def add_trip():

    get_conn()
    user_result = EMPTY_RESULT
    trip_result = EMPTY_RESULT

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)

    if not usr.exists:
        user_result = Result(None, "User does not exist")

    else:
        new_trip = Trip.from_strs("0",
                                  request.form.get('trip_start'),
                                  request.form.get('trip_end'))
        trip_result = usr.add_trip(new_trip)

    return render_template("user_trips.html",
                           current_mapshare_id=current_mapshare_id,
                           user_result=user_result,
                           trip_result=trip_result,
                           user_trips=usr.trips)


@app.route('/update_trip', methods=['POST'])
def update_trip():

    get_conn()
    user_result = EMPTY_RESULT
    trip_result = EMPTY_RESULT

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)

    if not usr.exists:
        user_result = Result(None, "User does not exist")

    else:
        trip = Trip.from_strs(request.form.get('trip_id'),
                              request.form.get('trip_start'),
                              request.form.get('trip_end'))
        trip_result = usr.update_trip(trip)

    return render_template("user_trips.html",
                           current_mapshare_id=current_mapshare_id,
                           user_result=user_result,
                           trip_result=trip_result,
                           user_trips=usr.trips)


@app.route('/delete_trip', methods=['POST'])
def delete_trip():

    get_conn()
    user_result = EMPTY_RESULT
    trip_result = EMPTY_RESULT

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)

    if not usr.exists:
        user_result = Result(None, "User does not exist")

    else:
        trip_id = request.form.get('trip_id')
        trip_result = usr.delete_trip(trip_id)

    return render_template("user_trips.html",
                           current_mapshare_id=current_mapshare_id,
                           user_result=user_result,
                           trip_result=trip_result,
                           user_trips=usr.trips)
