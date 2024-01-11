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


@app.route('/admin')
def admin():
    return render_template("admin.html", result=EMPTY_RESULT)


@app.route('/change_mapshare_pw', methods=['POST'])
def change_mapshare_pw():
    pass


@app.route('/delete_user', methods=['POST'])
def delete_user():
    get_conn()

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    entered_mapshare_id = request.form.get('confirmation_id')

    usr = User(mapshare_id=current_mapshare_id)
    user_result = usr.exists()
    if not user_result.status:
        return render_template("users.html", result=user_result)

    if entered_mapshare_id == current_mapshare_id:
        return render_template("users.html", result=usr.delete())

    delete_res = Result(False, "Mapshare ID does not match")

    return render_template("user_settings.html",
                           user_result=user_result,
                           radius_result=EMPTY_RESULT,
                           state_result=EMPTY_RESULT,
                           trip_result=EMPTY_RESULT,
                           delete_result=delete_res,
                           user=usr)


@app.route('/register', methods=['POST'])
def register():

    get_conn()

    usr = User(request.form.get('mapshare_id'),
               request.form.get('mapshare_password'))
    register_result = usr.register(debug=False)

    return render_template("admin.html", result=register_result)


@app.route('/set_user_alert_radius', methods=['POST'])
def set_user_alert_radius():

    get_conn()

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)
    user_result = usr.exists()

    radius = request.form.get('usr_alert_radius')
    radius_res = usr.update_alert_radius_setting(radius)

    return render_template("user_settings.html",
                           user_result=user_result,
                           radius_result=radius_res,
                           state_result=EMPTY_RESULT,
                           trip_result=EMPTY_RESULT,
                           delete_result=EMPTY_RESULT,
                           user=usr)


@app.route('/update_user_states', methods=['POST'])
def update_user_states():

    get_conn()

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)
    user_result = usr.exists()

    states = request.form.getlist('user_states')
    state_res = usr.update_state_setting(states)

    return render_template("user_settings.html",
                           user_result=user_result,
                           radius_result=EMPTY_RESULT,
                           state_result=state_res,
                           trip_result=EMPTY_RESULT,
                           delete_result=EMPTY_RESULT,
                           user=usr)


@app.route('/set_aqi_key', methods=['POST'])
def set_aqi_key():

    aqi_result = EMPTY_RESULT
    airnow_key = request.form.get('airnow_key')

    # test the given key
    # todo: put this operation somewhere else
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

    return render_template("admin.html", result=aqi_result)


@app.route('/users')
def users():
    return render_template("users.html", result=EMPTY_RESULT)


@app.route('/load_user_settings', methods=['POST'])
def load_user_settings():

    get_conn()

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)
    user_result = usr.exists()

    if user_result.status:

        return render_template("user_settings.html",
                               user_result=user_result,
                               radius_result=EMPTY_RESULT,
                               state_result=EMPTY_RESULT,
                               trip_result=EMPTY_RESULT,
                               delete_result=EMPTY_RESULT,
                               user=usr)
    else:

        return render_template("users.html", result=user_result)


@app.route('/add_trip', methods=['POST'])
def add_trip():

    get_conn()

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)
    user_result = usr.exists()

    new_trip = Trip.from_strs("0",
                              request.form.get('trip_state'),
                              request.form.get('trip_start'),
                              request.form.get('trip_end'))
    trip_result = usr.add_trip(new_trip)

    return render_template("user_settings.html",
                           user_result=user_result,
                           radius_result=EMPTY_RESULT,
                           state_result=EMPTY_RESULT,
                           trip_result=trip_result,
                           delete_result=EMPTY_RESULT,
                           user=usr)


@app.route('/update_trip', methods=['POST'])
def update_trip():

    get_conn()

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')
    usr = User(mapshare_id=current_mapshare_id)
    user_result = usr.exists()
    trip = Trip.from_strs(request.form.get('trip_id'),
                          request.form.get('trip_state'),
                          request.form.get('trip_start'),
                          request.form.get('trip_end'))
    trip_result = usr.update_trip(trip)

    return render_template("user_settings.html",
                           user_result=user_result,
                           radius_result=EMPTY_RESULT,
                           state_result=EMPTY_RESULT,
                           trip_result=trip_result,
                           delete_result=EMPTY_RESULT,
                           user=usr)


@app.route('/delete_trip', methods=['POST'])
def delete_trip():

    get_conn()

    # get user form data
    current_mapshare_id = request.form.get('mapshare_id')

    usr = User(mapshare_id=current_mapshare_id)
    user_result = usr.exists()
    trip_id = request.form.get('trip_id')
    trip_result = usr.delete_trip(trip_id)

    return render_template("user_settings.html",
                           user_result=user_result,
                           radius_result=EMPTY_RESULT,
                           state_result=EMPTY_RESULT,
                           trip_result=trip_result,
                           delete_result=EMPTY_RESULT,
                           user=usr)
