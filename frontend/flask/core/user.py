from .db import db_submit, db_extract
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


qrys = SqlQueries()

MAPSHARE_EXISTS = Result(False, 'Mapshare ID already in use.')
REG_SUCCESS = Result(True, 'Check your satphone for confirmation.')
INVALID_CREDS = Result(False, 'Registration Failed. Invalid Credentials.')


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

    def _update_mapshare_pw(self, new_pw):
        pass

    def _get_user_id(self):
        return db_extract(qrys.select_user_id,
                          self.credentials)[0][0]

    def get_mapshare_id(self):
        return self.credentials['mapshare_id']

    def exists(self):
        return bool(self.user_id)

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

        # send success message
        return REG_SUCCESS

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

    def _send_registration_confirmation(self):
        # I wasn't able to figure out a
        # way to get the garmin_device_id other than to
        # send a message to the device and pull data from the request body.
        success_msg = "Registration Successful!"
        return self._send_message(self.credentials, success_msg)
