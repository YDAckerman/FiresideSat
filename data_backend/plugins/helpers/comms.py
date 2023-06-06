
from helpers.sql_queries import SqlQueries
from helpers.api_endpoint import ApiEndpoint
import json
import base64

# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC


class Comms():

    incident_report_columns = ["user_id", "incident_id",
                               "incident_last_update",
                               "aqi_last_update",
                               "incident_behavior",
                               "incident_name",
                               "perimeter_lon",
                               "perimeter_lat",
                               "centroid_lon",
                               "centroid_lat",
                               "aqi_max",
                               "aqi_obs_lon",
                               "aqi_obs_lat"]

    def __init__(self, http_hook, pg_hook):
        print("using comms")
        self.sql = SqlQueries()
        self.api = ApiEndpoint()
        self.http_hook = http_hook
        self.pg_hook = pg_hook

    def send_messages(self, service_name, message_type, context, log):

        pg_conn = self.pg_hook.get_conn()
        pg_cur = self.pg_conn.cursor()
        current_date = context.get('data_interval_start')

        if message_type == "trip_state":

            pg_cur.execute(self.sql.select_state_change_users,
                           [current_date]*3)
            records = pg_cur.fetchall()

            for record in records:

                usr, pw, start_date, end_date, device_id, state = record
                msg = f'{state} incident reports for {usr} ' \
                    + f'for trip dates {start_date} to {end_date}'

                data = self._make_data_obj(device_id, msg)
                endpoint = self.api.format_endpoint("send_message_endpoint",
                                                    {'mapshare_id': usr})
                headers = self.make_headers('', pw)

                try:
                    response = self.http_hook.run(endpoint=endpoint,
                                                  headers=headers,
                                                  json=data)
                    if json.loads(response.text)["success"]:
                        log.info(f'{state} message successfully '
                                 + f'sent to {usr} at {current_date}')
                    else:
                        log.info(f'There was an error sending {state} message'
                                 + f'to {usr} at {current_date}')
                except Exception as e:
                    log.info(e)

        elif message_type == "incident_report":

            pg_cur.execute(self.sql.select_user_incidents,
                           [current_date]*2)
            records = pg_cur.fetchall()

            for record in records:

                report_info = dict(zip(self.incident_report_columns, record))

                pg_cur.execute(self.sql.insert_incident_reports,
                               report_info)

            # need to add a filter in sql that removes entries if the user
            # has been sent a report for a given incident_id, last_update
            # (user_id, incident_id, last_update, aqi_last_update)

            pass

        else:

            raise ValueError("Unrecognized message type")

        pg_conn.commit()
        pg_conn.close()

    @staticmethod
    def _make_data_obj(device_id, msg):
        return {'deviceIds': device_id,
                'fromAddr': 'noreply@firesidesat.com',
                'messageText': msg}

    @staticmethod
    def _make_incident_report(record):
        msg = 'Incident Name: {incident_name} ' \
            + 'Last Update: {incident_last_update} ' \
            + 'Incident Behavior: {incident_behavior} ' \
            + 'Centroid (lon,lat): ({centroid_lon},{centroid_lat} ' \
            + 'Nearest Point (lon,lat): ({perimeter_lon},{perimeter_lat}) ' \
            + 'Max AQI: {max_aqi} ' \
            + 'AQI Location (lon, lat): ({aqi_obs_lon}, {aqi_obs_lat})'

        return msg.format(record)

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
