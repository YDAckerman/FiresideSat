from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .result import Result
import re
import random


class Device():

    OTP_LEN = 6
    OTP_LOWER, OTP_UPPER = (0, 9)

    def __init__(self):
        self.garmin_id = None

    def set_id(self, garmin_id):
        self.garmin_id = garmin_id

    def send_otp(self, usr):

        otp = ''.join([str(random.randint(self.OTP_LOWER,
                                          self.OTP_UPPER))
                       for _ in range(self.OTP_LEN)])
        post_params = self._send_user_message(usr, otp)
        if post_params:
            usr.set_otp(otp)
            self.set_id(self._extract_device_id(post_params))
            return Result(True, 'OTP successfully sent')
        return Result(False, 'Message failed to send')

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
