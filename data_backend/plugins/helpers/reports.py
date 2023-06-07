from helpers.api_endpoint import ApiEndpoint, make_headers


class Report:

    def __init__(self, record, record_cols, message_template):

        self.report_data = self._make_report_data(record, record_cols)
        self.message = self.format_template(message_template)

    def format_template(self, template):
        return template.format(**self.report_data)

    def get_recipient(self):
        return self.report_data['user_id']

    def send(self, http_hook, log):
        try:
            return http_hook.run(**self._get_post_parameters)
        except Exception as e:
            log.info(e)

    def record(self, pg_cur, sql):
        pg_cur.execute(sql, self.report_data)

    def _make_report_data(self, record, record_cols):

        if len(record_cols) is not len(record):

            raise ValueError("Record names are misaligned.")

        report_data = dict(zip(record_cols, record))
        report_data_keys = report_data.keys()

        if 'mapshare_pw' not in report_data_keys or \
           'device_id' not in report_data_keys:

            raise ValueError("Record has insufficient data.")

        return report_data

    def _get_post_endpoint(self):
        return ApiEndpoint().format_endpoint(
            "send_message_endpoint",
            {'mapshare_id': self.report_data['mapshare_id']}
        )

    def _get_post_headers(self):
        return make_headers('', self.report_data['mapshare_pw'])

    def _get_post_json(self):
        return {
            'deviceIds': self.report_data['device_id'],
            'fromAdd': 'noreply@firesidesat.com',
            'messageText': self.message
        }

    def _get_post_parameters(self):
        return {
            'json': self._get_post_json(),
            'endpoint': self._get_post_endpoint(),
            'headers': self._get_post_headers()
        }


def trip_state_reporter():

    columns = ["user_id",
               "mapshare_id",
               "mapshare_pw",
               "start_date",
               "end_date",
               "device_id",
               "state",
               "date_sent"]

    message_template = '{state} incident reports ' \
        + 'for trip dates {start_date} to {end_date}'

    def make_trip_state_report(record):
        return Report(record, columns, message_template)

    return trip_state_reporter


def incident_reporter():

    columns = ["user_id", "incident_id",
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
               "aqi_obs_lat",
               "mapshare_id",
               "mapshare_pw",
               "garmin_device_id"]

    message_template = 'Incident Name: {incident_name} ' \
        + 'Last Update: {incident_last_update} |' \
        + 'Incident Behavior: {incident_behavior} |' \
        + 'Centroid (lon,lat): ({centroid_lon},{centroid_lat} |' \
        + 'Nearest Point (lon,lat): ' \
        + '({perimeter_lon},{perimeter_lat}) |' \
        + 'Max AQI: {max_aqi} |' \
        + 'AQI Location (lon, lat): ({aqi_obs_lon}, {aqi_obs_lat})'

    def make_incident_report(record):
        return Report(record, columns, message_template)

    return make_incident_report
