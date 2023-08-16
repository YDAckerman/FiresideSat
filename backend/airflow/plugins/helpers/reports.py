from helpers.header_funs import get_auth_basic


class Report:

    def __init__(self, record, record_cols, message_template, save_sql):

        self.report_data = self._make_report_data(record, record_cols)
        self.message = self.format_template(message_template)
        self.save_sql = save_sql

    def send(self, endpoint, test=False):

        endpoint.set_route(user=self.report_data['mapshare_id'])
        headers = get_auth_basic('', self.report_data['mapshare_pw'])
        json = self._make_json()

        if test:
            print(json)
            return None

        return endpoint.post(json=json, headers=headers)

    def save(self, pg_cur):
        pg_cur.execute(self.save_sql, self.report_data)

    def format_template(self, template, **kwargs):
        return template.format(**self.report_data, **kwargs)

    def get_recipient(self):
        return self.report_data['user_id']

    def _make_report_data(self, record, record_cols):

        if len(record_cols) is not len(record):
            """
            NOTE: does not check that the record values have the correct
                  type/format/anything
            TODO: safety?
            """
            raise ValueError("Record names are misaligned.")

        report_data = dict(zip(record_cols, record))

        return report_data

    def _make_json(self):
        return {
            'deviceIds': self.report_data['device_id'],
            'fromAddr': 'noreply@firesidesat.com',
            'messageText': self.message
        }

    # def _make_endpoint(self):

    #     return ApiEndpoint().format_endpoint(
    #         "send_message_endpoint",
    #         {'mapshare_id': }
    #     )
