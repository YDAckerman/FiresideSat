from helpers.sql_queries import SqlQueries
from helpers.header_funs import get_auth_basic


class Report:

    def __init__(self, record, record_cols, message_template, save_sql):

        self.report_data = self._make_report_data(record, record_cols)
        self.message = self.format_template(message_template)
        self.save_sql = save_sql

    def send(self, endpoint, test=False):

        if test:
            return None

        endpoint.set_route(mapshare_id=self.report_data['mapshare_id'])
        headers = get_auth_basic('', self.report_data['mapshare_pw'])
        json = self._make_json()
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


class ReportFactory():

    failure_message = "{report_type} message failed to send " \
        + "to {user_id} on {current_date}"

    sql = SqlQueries()

    # There is some redundancy here, but I think it adds clarity
    reports_dict = {

        "trip_state_report": {
            'columns': ["user_id",
                        "mapshare_id",
                        "mapshare_pw",
                        "trip_id",
                        "start_date",
                        "end_date",
                        "device_id",
                        "state",
                        "date_sent"],
            'message_template': '{state} incident reports '
            + 'for trip dates {start_date} to {end_date}',
            'message_header': '',
            'records_sql': sql.select_state_change_users,
            'save_sql': sql.insert_trip_state_report
        },

        'incident_report': {
            'columns': ["user_id", "incident_id",
                        "incident_last_update",
                        "aqi_last_update",
                        "total_acres",
                        "incident_behavior",
                        "incident_name",
                        # "perimeter_lon",
                        # "perimeter_lat",
                        "centroid_lon",
                        "centroid_lat",
                        "max_aqi",
                        "aqi_obs_lon",
                        "aqi_obs_lat",
                        "mapshare_id",
                        "mapshare_pw",
                        "device_id"],
            'message_template': '{incident_name}|'
            + '{incident_last_update}|'
            + 'acres:{total_acres}|'
            + 'c:{centroid_lat},{centroid_lon}|'
            # + 'e:{perimeter_lat},{perimeter_lon}|'
            + 'aqi:{max_aqi}',
            'records_sql': sql.select_user_incidents,
            'save_sql': sql.insert_incident_report
        }
    }

    def __init__(self, report_type, date_sent):
        self.report_type = report_type
        self.report_metadata = self.reports_dict[report_type]
        self.date_sent = date_sent

    def make_report(self, record):

        return Report(record,
                      self.report_metadata['columns'],
                      self.report_metadata['message_template'],
                      self.report_metadata['save_sql'])

    def get_failure_message(self):
        return self.failure_message.format(
            report_type=self.report_type,
            user_id=self.report.get_recipient(),
            current_date=self.date_sent)

    def get_records_sql(self):
        return self.report_metadata['records_sql']

    def get_save_sql(self):
        return self.report_metadata['save_sql']
