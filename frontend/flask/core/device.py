from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .result import Result, RESULT_DB_ERR
from .sql_queries import SqlQueries
import requests
from pykml import parser
import re
import random

qrys = SqlQueries()


class Device():

    OTP_LEN = 6
    OTP_LOWER, OTP_UPPER = (0, 9)

    def __init__(self, device_id=None, garmin_id=None, imei=None):
        self.device_id = device_id
        self.garmin_id = garmin_id
        self.imei = imei

    def set_garmin_id(self, garmin_id):
        self.garmin_id = garmin_id

    def set_device_id(self, device_id):
        self.device_id = device_id

    def set_imei(self, usr):
        mapshare_id, mapshare_pw = list(usr.credentials.values())
        url = f'https://share.garmin.com/Feed/Share/{mapshare_id}'
        resp = requests.get(url, auth=(mapshare_id, mapshare_pw))
        root = parser.fromstring(bytes(resp.text, encoding='utf8'))
        self.imei = root.Document.Folder.Placemark.ExtendedData.Data[6].value

    def send_otp(self, usr):

        otp = ''.join([str(random.randint(self.OTP_LOWER,
                                          self.OTP_UPPER))
                       for _ in range(self.OTP_LEN)])
        post_params = self._send_user_message(usr, otp)
        if post_params:
            usr.set_otp(otp)
            self.set_garmin_id(self._extract_device_id(post_params))
            return Result(True, 'OTP successfully sent')
        return Result(False, 'Message failed to send')

    def register(self, usr, conn):

        try:
            self.set_imei(usr)
        except Exception as e:
            print("Set Device IMEI Error: " + e)
            return Result(False, 'Problem getting device IMEI')

        with conn:
            with conn.cursor() as cur:

                try:

                    cur.execute(qrys.new_device,
                                {"user_id": usr.user_id,
                                 'garmin_device_id': self.garmin_id,
                                 'garmin_imei': self.imei})
                    self.set_device_id(cur.fetchall()[0][0])

                except Exception as e:
                    print("Insert Device Error: " + e)
                    return RESULT_DB_ERR

        conn.commit()

        return Result(True, 'Device Registration Successful')

    def send_confirmation(self, usr):

        msg = "Registration Successful"
        post_params = self._send_user_message(usr, msg)
        if post_params:
            self.set_garmin_id(self._extract_device_id(post_params))
            return Result(True, 'Check your satphone for confirmation.')
        return Result(False, 'Registration failed. ',
                      'Double check your credentials.')

    @staticmethod
    def _send_user_message(usr, msg):

        try:

            fireFoxOptions = webdriver.FirefoxOptions()
            fireFoxOptions.add_argument('--headless')

            browser = webdriver.Firefox(options=fireFoxOptions)
            browser.get("https://share.garmin.com/"
                        + f"share/{usr.credentials['mapshare_id']}")

            password = browser.find_element(By.ID, "mapsharePassword")
            password.send_keys(usr.credentials['mapshare_pw'])
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
                + f"/{usr.credentials['mapshare_id']}/Map/" \
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
