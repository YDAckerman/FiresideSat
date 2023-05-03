from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Comms():

    def __init__(self):
        print("using comms")

    @staticmethod
    def send_user_message(usr, pw, msg, log):

        pass

    @staticmethod
    def get_user_messages(usr, pw, log):

        try:

            fireFoxOptions = webdriver.FirefoxOptions()
            fireFoxOptions.add_argument("headless")

            browser = webdriver.Firefox()

            browser.get(f"https://share.garmin.com/share/{usr}")
            password = browser.find_element(By.ID, "mapsharePassword")
            password.send_keys(pw)

            browser.find_element(By.ID, "btn-mapshare-password-submit").click()

            WebDriverWait(browser, 20) \
                .until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div[data-test-id='UserMessagesRow']")
                )) \
                .click()

            date_css = "span.lbl-time.server-time"
            message_dates = [e.text for e in browser
                             .find_elements(By.CSS_SELECTOR,
                                            date_css)]

            msg_css = "div.user-message-content-container"
            message_contents = [e.text for e in browser
                                .find_elements(By.CSS_SELECTOR,
                                               msg_css)]

        except Exception:
            log.info(f"There was an error getting messages from {usr}")
            return [(None, None)]

        return zip(message_dates, message_contents)
