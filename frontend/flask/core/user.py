from .db import db_submit, db_extract
from .device import Device
from .result import Result
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

    device = None
    trips = []

    def __init__(self,
                 mapshare_id=None,
                 mapshare_password=None):

        self.credentials = {
            "mapshare_id": mapshare_id,
            "mapshare_pw": mapshare_password
        }

        self.is_registered = self.check_is_registered()

    def _update_mapshare_pw(self, new_pw):
        pass

    def _register(self):
        return db_submit(qrys.insert_new_usr,
                         self.credentials,
                         Result(True, "User Successfully Added To DB"))

    def _get_user_id(self):
        return db_extract(qrys.select_user_id,
                          self.credentials)[0][0]

    def check_is_registered(self):
        return bool(db_extract(qrys.does_user_exist,
                               self.credentials))

    def delete(self):
        return db_submit(qrys.delete_user,
                         self.credentials,
                         Result(True, 'User Successfully Deleted From DB'))

    def register(self, debug=False):

        if self.is_registered:
            return MAPSHARE_EXISTS

        # attempt to get the device IMEI
        device_imei = self._get_device_imei(self.credentials)

        if device_imei is None:
            return INVALID_CREDS

        # attempt to send a confirmation message
        # and extract the device id from the response:
        if debug:
            device_garmin_id = "000000"
        else:
            msg_resp = self._send_registration_confirmation()
            if msg_resp is None:
                return INVALID_CREDS
            device_garmin_id = self._extract_device_id(msg_resp)

        # register the user to the database
        self._register()

        # assign the device to the user
        self.device = Device(device_garmin_id, device_imei)

        # register the device to the database
        dev_reg_res = self.device.register_to_user(self._get_user_id())
        if not dev_reg_res.status:
            return dev_reg_res

        # send success message
        return REG_SUCCESS

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
        return root.Document.Folder.Placemark.ExtendedData.Data[6].value

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
    def _extract_device_id(post_params):
        device_id_part = post_params.decode("UTF-8").split("&")[0]
        return re.findall(r'\d+', device_id_part)[0]

    def _send_registration_confirmation(self):
        # I wasn't able to figure out a
        # way to get the garmin_device_id other than to
        # send a message to the device and pull data from the request body.
        success_msg = "Registration Successful!"
        return self._send_message(self.credentials, success_msg)
