from .db import db_submit, db_submit_many, db_extract
from .result import Result
from .trip import Trip
from .sql_queries import SqlQueries

from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
from pykml import parser
import re
import math


qrys = SqlQueries()

# Numeric constants
METERS_PER_MILE = 1609.344
MILES_PER_METER = 0.0006213712

# possible results
MAPSHARE_EXISTS = Result(False, 'Mapshare ID already in use.')
REG_SUCCESS = Result(True, 'Check your satphone for confirmation.')
INVALID_CREDS = Result(False, 'Registration Failed. Invalid Credentials.')
USR_DOES_NOT_EXIST = Result(False, "User does not exist")
TRIPS_OVERLAP = Result(False, "Trips Cannot Overlap")
TRIP_BAD_DATE_ORDER = Result(False, "Trips Must Start Before They End")
TRIP_ADDED = Result(True, "Trip Added")
EMPTY_RESULT = Result(None, "")


class User():

    user_id = 0
    device_id = 0
    trips = []

    def __init__(self,
                 mapshare_id=None,
                 mapshare_password=None):

        self.credentials = {
            "mapshare_id": mapshare_id,
            "mapshare_pw": mapshare_password
        }

        self.user_id = self._get_user_id()
        if self.user_id:
            self.device_id = self._get_device_id()
            self._get_trips()
            self._get_radius()
            self._get_states()

    # -#-------------------------------------------------------------------#- #
    # -      public methods                                                 - #
    # -#-------------------------------------------------------------------#- #

    def get_radius(self):
        return self.radius_mi

    def get_states(self):
        return self.states

    def get_mapshare_id(self):
        return self.credentials['mapshare_id']

    def get_trips(self):
        return self.trips

    def update_alert_radius_setting(self, radius_miles):

        if not self._exists:
            return EMPTY_RESULT

        del_res = db_submit(qrys.delete_alert_radius_setting,
                            {'user_id': self.user_id},
                            Result(True, "Alert Settings Deleted"))

        if not del_res.status:
            return del_res

        radius_meters = float(radius_miles) * METERS_PER_MILE
        submit_res = db_submit(qrys.insert_alert_radius,
                               {'user_id': self.user_id,
                                'radius': radius_meters},
                               Result(True, 'Alert Radius Updated'))

        if submit_res.status:
            self.radius_mi = radius_miles

        return submit_res

    def update_state_setting(self, states):

        if not self._exists:
            return EMPTY_RESULT

        del_res = db_submit(qrys.delete_state_settings,
                            {'user_id': self.user_id},
                            Result(True, "State Settings Deleted"))

        if not del_res.status:
            return del_res

        data = [(self.user_id, 'include_state', state) for state in states]
        submit_res = db_submit_many(qrys.insert_state_settings, data,
                                    Result(True, "State Settings Updated"))

        if submit_res.status:
            self.states = states

        return submit_res

    def add_trip(self, new_trip):

        if not self._exists:
            return EMPTY_RESULT

        check_overlap = [t.intersects(new_trip) for t in self.trips]

        if sum(check_overlap) != 0:
            return TRIPS_OVERLAP

        if not new_trip.consistent():
            return TRIP_BAD_DATE_ORDER

        db_res = db_submit(qrys.insert_new_trip,
                           {'user_id': self.user_id,
                            'device_id': self.device_id,
                            'start_date': new_trip.start_date,
                            'end_date': new_trip.end_date},
                           TRIP_ADDED)

        if db_res.status:
            self._get_trips()

        return db_res

    def delete_trip(self, trip_id):

        if not self._exists:
            return EMPTY_RESULT

        db_res = db_submit(qrys.delete_trip,
                           {'trip_id': trip_id},
                           Result(True, "Trip Deleted"))

        if db_res.status:
            self._get_trips()

        return db_res

    def update_trip(self, trip):

        if not self._exists:
            return EMPTY_RESULT

        check_overlap = [t.intersects(trip) for t in self.trips
                         if t.trip_id != trip.trip_id]

        if sum(check_overlap) != 0:
            return Result(None, "Trips Cannot Overlap")

        if not trip.consistent():
            return Result(None, "Trips Must Start Before They End")

        db_res = db_submit(qrys.update_trip,
                           {'trip_id': trip.trip_id,
                            'start_date': trip.start_date,
                            'end_date': trip.end_date},
                           Result(True, "Trip Updated"))

        if db_res.status:
            self._get_trips()

        return db_res

    def exists(self):
        if self._exists():
            return Result(True, "Editing Data for Mapshare" +
                          f" ID: {self.credentials['mapshare_id']}")
        else:
            return USR_DOES_NOT_EXIST

    def delete(self):
        return db_submit(qrys.delete_user,
                         {'user_id': self.user_id},
                         Result(True, 'User Successfully Deleted'))

    def register(self, debug=False):

        if self.user_id:
            return MAPSHARE_EXISTS

        # attempt to get the device IMEI
        device_imei = self._get_device_imei(self.credentials)

        if device_imei is None:
            return INVALID_CREDS

        # attempt to send a confirmation message
        # and extract the device id from the response:
        if debug:
            garmin_id = "000000"
        else:
            msg_resp = self._send_registration_confirmation()
            if msg_resp is None:
                return INVALID_CREDS
            garmin_id = self._extract_garmin_id(msg_resp)

        # register the user to the database and
        # populate their user_id
        usr_reg_res = self._register()
        if not usr_reg_res:
            return usr_reg_res
        self.user_id = self._get_user_id()

        # register the device to the database
        # and populate the device_id
        dev_reg_res = self._register_device(garmin_id, device_imei)
        if not dev_reg_res.status:
            # if something went wrong, delete the
            # row from the user table
            self.delete()
            return dev_reg_res
        self.device_id = self._get_device_id()

        # set state and alert radius defaults
        settings_res = self._set_default_settings()
        if not settings_res.status:
            return settings_res

        # send success message
        return REG_SUCCESS

    def update_mapshare_pw(self, new_pw):
        pass

    # -#-----------------------------------------------------------------#- #
    # -      private methods                                              - #
    # -#-----------------------------------------------------------------#- #

    def _exists(self):
        return bool(self.user_id)

    def _get_user_id(self):
        return db_extract(qrys.select_user_id,
                          self.credentials)[0][0]

    def _get_trips(self):

        trip_data = db_extract(qrys.select_user_trips,
                               {'user_id': self.user_id})
        if trip_data:
            self.trips = [Trip(*datum) for datum in trip_data]

    def _get_radius(self):

        radius_mt_str = db_extract(qrys.get_alert_radius_setting,
                                   {'user_id': self.user_id})[0][0]
        if radius_mt_str:
            self.radius_mi = math.floor(float(radius_mt_str) * MILES_PER_METER)

    def _get_states(self):

        states = db_extract(qrys.get_state_settings,
                            {'user_id': self.user_id})

        if states:
            self.states = [state[0] for state in states]
        else:
            self.states = []

    def _set_default_settings(self):

        return db_submit(qrys.insert_default_settings,
                         self.user_id,
                         Result(True, "User Settings Added"))

    def _register(self):
        return db_submit(qrys.insert_new_usr,
                         self.credentials,
                         Result(True, "User Successfully Added To DB"))

    def _register_device(self, garmin_id, device_imei):

        return db_submit(qrys.insert_new_device,
                         {'user_id': self.user_id,
                          'garmin_imei': device_imei,
                          'garmin_device_id': garmin_id},
                         Result(True, "Device Successfully Registered"))

    def _get_device_id(self):
        return db_extract(qrys.select_device_id,
                          {'user_id': self.user_id})[0][0]

    def _send_registration_confirmation(self):
        # I wasn't able to figure out a
        # way to get the garmin_device_id other than to
        # send a message to the device and pull data from the request body.
        success_msg = "Registration Successful!"
        return self._send_message(self.credentials, success_msg)

    @staticmethod
    def _get_device_imei(credentials):

        BAD_RESP = ['',
                    'You do not have permission'
                    ' to view this directory or page.']

        mapshare_id = credentials['mapshare_id']
        mapshare_pw = credentials['mapshare_pw']

        url = f'https://share.garmin.com/Feed/Share/{mapshare_id}'
        resp = requests.get(url, auth=(mapshare_id, mapshare_pw))
        if resp.text in BAD_RESP:
            return None
        root = parser.fromstring(bytes(resp.text, encoding='utf8'))
        return str(root
                   .Document
                   .Folder
                   .Placemark
                   .ExtendedData
                   .Data[6]
                   .value)

    @staticmethod
    def _send_message(credentials, msg):

        mapshare_id = credentials['mapshare_id']
        mapshare_pw = credentials['mapshare_pw']

        try:

            fireFoxOptions = webdriver.FirefoxOptions()
            fireFoxOptions.add_argument('--headless')

            browser = webdriver.Firefox(options=fireFoxOptions)
            browser.get("https://share.garmin.com/"
                        + f"share/{mapshare_id}")

            password = browser.find_element(By.ID, "mapsharePassword")
            password.send_keys(mapshare_pw)
            browser.find_element(By.ID, "btn-mapshare-password-submit").click()

            WebDriverWait(browser, 20) \
                .until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div[data-test-id='topBtnMessage']")
                )) \
                .click()

            message = browser.find_element(By.ID, "messageFrom")
            message.send_keys("no.reply@firesidesat.com")

            message = browser.find_element(By.ID, "textMessage")
            message.send_keys(msg)

            WebDriverWait(browser, 20) \
                .until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "button[data-test-id='MessageUserSend']")
                )) \
                .click()

            post_params = None
            post_url = "https://share.garmin.com" \
                + f"/{mapshare_id}/Map/" \
                + "SendMessageToDevices"
            for req in browser.requests:
                if req.url == post_url:
                    post_params = req.body
                    break
                else:
                    next

            browser.close()
            return post_params

        except Exception as e:
            print(e)
            return None

    @staticmethod
    def _extract_garmin_id(post_params):
        device_id_part = post_params.decode("UTF-8").split("&")[0]
        return re.findall(r'\d+', device_id_part)[0]
