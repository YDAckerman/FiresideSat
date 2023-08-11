from helpers.reports import ReportFactory
from helpers.endpoint import Endpoint
from helpers.endpoint_templates import SEND_MESSAGE_TEMPLATE
import json

# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC

# MAX_DIST_M = 1220000
MAX_DIST_M = 354055 # meters


class CommsProcess():

    def __init__(self, http_hook, pg_hook):
        self.http_hook = http_hook
        self.pg_hook = pg_hook

    def send_messages(self, report_type, context, log):

        endpoint = Endpoint(self.http_hook,
                            'send_message',
                            SEND_MESSAGE_TEMPLATE)

        pg_conn = self.pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        current_date = context.get('ds')

        report_factory = ReportFactory(report_type, current_date)

        pg_cur.execute(report_factory.get_records_sql(),
                       {'current_date': current_date,
                        'max_distance_m': MAX_DIST_M})

        report_records = pg_cur.fetchall()
        for record in report_records:

            report = report_factory.make_report(record)
            endpt_resp = report.send(endpoint)

            if endpt_resp and json.loads(endpt_resp.text)['success']:

                report.save(pg_cur)

            else:

                log.info(report_factory.get_failure_message())

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
