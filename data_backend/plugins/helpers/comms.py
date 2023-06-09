from helpers.sql_queries import SqlQueries
from helpers.reports import ReportFactory
import json


# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC


class Comms():

    failure_message = "{message_type} message failed to send " \
        + "to {user_id} on {current_date}"

    def __init__(self, http_hook, pg_hook):
        print("using comms")
        self.sql = SqlQueries()
        self.http_hook = http_hook
        self.pg_hook = pg_hook

    def send_messages(self, message_type, context, log):

        pg_conn = self.pg_hook.get_conn()
        pg_cur = self.pg_conn.cursor()
        current_date = context.get('data_interval_start')

        report_factory = ReportFactory(message_type)

        if message_type == "trip_state_report":

            pg_cur.execute(self.sql.select_state_change_users,
                           {'current_date': current_date})
            records = pg_cur.fetchall()
            mark_sent_sql = self.sql.insert_trip_state_report

        elif message_type == "incident_report":

            pg_cur.execute(self.sql.select_user_incidents,
                           {'current_date': current_date,
                            'max_distance_m': 1220000})
            records = pg_cur.fetchall()
            mark_sent_sql = self.sql.insert_incident_report

        for record in records:

            report = report_factory.generate_from(record)
            http_resp = report.send(self.http_hook, log)
            post_successful = json.loads(http_resp.text)["success"]

            if not post_successful:

                log.info(self
                         .failure_message
                         .format(message_type=message_type,
                                 user_id=report.get_recipient(),
                                 current_date=current_date))

            else:

                report.mark_sent(pg_cur, mark_sent_sql)

        pg_conn.commit()
        pg_conn.close()

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
