from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re


class Comms:

    def __init__(self):
        pass

    @staticmethod
    def send_user_message(usr, pw, msg):

        try:

            fireFoxOptions = webdriver.FirefoxOptions()
            fireFoxOptions.add_argument('--headless')

            browser = webdriver.Firefox(options=fireFoxOptions)
            browser.get(f"https://share.garmin.com/share/{usr}")

            password = browser.find_element(By.ID, "mapsharePassword")
            password.send_keys(pw)
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

            request_body = None
            post_url = f'https://share.garmin.com/{usr}/Map/' \
                + 'SendMessageToDevices'
            for req in browser.requests:
                if req.url == post_url:
                    request_body = req.body
                    break
                else:
                    next

            browser.close()
            return request_body

        except Exception as e:
            print(e)
            return None

    @staticmethod
    def extract_device_id(request_body):
        device_id_part = request_body.decode("UTF-8").split("&")[0]
        return re.findall(r'\d+', device_id_part)[0]
