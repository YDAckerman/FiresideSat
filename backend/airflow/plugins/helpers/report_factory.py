from helpers.report_templates import REPORTS_DICT
from helpers.reports import Report


class ReportFactory():

    current_report = None

    failure_message = "{report_type} message failed to send " \
        + "to user no. {user_id} on {current_date}"

    # There is some redundancy here, but I think it adds clarity

    def __init__(self, report_type, date_sent):
        self.report_type = report_type
        self.report_metadata = REPORTS_DICT[report_type]
        self.date_sent = date_sent

    def make_report(self, record):
        self.current_report = Report(record,
                                     self.report_metadata['columns'],
                                     self.report_metadata['message_template'],
                                     self.report_metadata['save_sql'])
        return self.current_report

    def get_failure_message(self):

        if not self.current_report:
            raise ValueError("No report")

        return self.failure_message.format(
            report_type=self.report_type,
            user_id=self.current_report.get_recipient(),
            current_date=self.date_sent)

    def get_records_sql(self):
        return self.report_metadata['records_sql']

    def get_save_sql(self):
        return self.report_metadata['save_sql']
