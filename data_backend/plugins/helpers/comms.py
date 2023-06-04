from airflow.hooks.http_hook import HttpHook
from helpers.sql_queries import SqlQueries
from helpers.api_endpoint import ApiEndpoint
import json
import base64

# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC


class Comms():

    def __init__(self):
        print("using comms")
        self.sql = SqlQueries()
        self.api = ApiEndpoint()

    def send_messages(self, service_name, message_type, pg_hook, context, log):

        http_hook = HttpHook(method='POST', http_conn_id=service_name)
        pg_conn = pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        current_date = context.get('data_interval_start')

        if message_type == "trip_state":

            pg_cur.execute(self.sql.select_state_change_users,
                           [current_date]*2)
            records = pg_cur.fetchall()

            for record in records:

                usr, pw, start_date, end_date, device_id = record
                msg = f'{msg_head} incident reports for {usr}' \
                    + f'for trip dates {start_date} to {end_date}'

                data = self._make_message(device_id, msg)
                endpoint = self.api.format_endpoint("send_message_endpoint",
                                                    usr)
                headers = self.make_headers(usr, pw)
                response = http_hook.run(endpoint=endpoint,
                                         data=data,
                                         headers=headers)
                if json.loads(response.text)["success"]:
                    log.info(f'{msg_head} message successfully '
                             + f'sent to {usr} at {current_date}')
                else:
                    log.info(f'There was an error sending {msg_head} message'
                             + f'to {usr} at {current_date}')

        elif message_type == "incident_report":

            pass

        else:

            raise ValueError("Unrecognized message type")

    @staticmethod
    def _make_message(device_id, msg):
        return {'deviceIds': device_id,
                'fromAddr': 'firesidesat',
                'messageText': msg}

    @staticmethod
    def make_headers(usr, pw):
        usr_pw = f'{usr}:{pw}'
        b64_val = base64.b64encode(usr_pw.encode()).decode()
        return {"Authorization": "Basic %s" % b64_val}

    # @staticmethod
    # def _get_user_messages(usr, pw, log):

    #     try:

    #         fireFoxOptions = webdriver.FirefoxOptions()
    #         fireFoxOptions.add_argument("headless")

    #         browser = webdriver.Firefox()

    #         browser.get(f"https://share.garmin.com/share/{usr}")
    #         password = browser.find_element(By.ID, "mapsharePassword")
    #         password.send_keys(pw)

    #         browser.find_element(By.ID, "btn-mapshare-password-submit").click()

    #         WebDriverWait(browser, 20) \
    #             .until(EC.visibility_of_element_located(
    #                 (By.CSS_SELECTOR, "div[data-test-id='UserMessagesRow']")
    #             )) \
    #             .click()

    #         date_css = "span.lbl-time.server-time"
    #         message_dates = [e.text for e in browser
    #                          .find_elements(By.CSS_SELECTOR,
    #                                         date_css)]

    #         msg_css = "div.user-message-content-container"
    #         message_contents = [e.text for e in browser
    #                             .find_elements(By.CSS_SELECTOR,
    #                                            msg_css)]

    #     except Exception:
    #         log.info(f"There was an error getting messages from {usr}")
    #         return [(None, None)]

    #     return zip(message_dates, message_contents)
