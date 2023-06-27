from airflow.models import Variable
import base64


def make_headers(usr, pw):
    usr_pw = f'{usr}:{pw}'
    b64_val = base64.b64encode(usr_pw.encode()).decode()
    return {"Authorization": "Basic %s" % b64_val}


class ApiEndpoint():

    def __init__(self):
        print("using api endpoint")

    def format_endpoint(self, endpoint_name, context):

        if context is None:
            raise ValueError("Endpoints require context data")

        if endpoint_name == "wildfire_current_endpoint":

            return self._wfigs_current_incidents_endpoint

        elif endpoint_name == "wildfire_test_endpoint":

            return self._format_wildfire_test_endpoint(context)

        elif endpoint_name == "airnow_endpoint":

            api_key = Variable.get("airnow_api_key")
            return self._format_airnow_endpoint(context.get('lat'),
                                                context.get('lon'),
                                                context.get('radius_miles'),
                                                api_key)

        elif endpoint_name == "mapshare_feed_endpoint":

            return self._mapshare_feed_endpoint \
                       .format(user=context.get("mapshare_id"),
                               imei=context.get("garmin_imei"))

        elif endpoint_name == "send_message_endpoint":

            return self._send_message_endpoint \
                       .format(user=context.get("mapshare_id"))

        else:

            raise ValueError("Unrecognized enpoint")

    def _format_airnow_endpoint(self, lat, lon, radius_miles, api_key):

        return self \
            ._airnow_radius_endpoint \
            .format(lat=lat, lon=lon,
                    radius_miles=radius_miles, key=api_key)

    def _format_wildfire_test_endpoint(self, context):

        current_date = context.get('data_interval_start')
        start_date = current_date.to_date_string()
        end_date = current_date \
            .add(days=1) \
            .to_date_string()

        return self._wfigs_test_incidents_endpoint \
                   .format(start_date, end_date)

    _airnow_bbox_endpoint = "https://airnowapi.org/aq/data/" \
        + "?startDate={year}-{month}-{day}T{hour_start}" \
        + "&endDate={year}-{month}-{day}T{hour_end}" \
        + "&parameters=PM25" \
        + "&BBOX={bbox}" \
        + "&datatype=A" \
        + "&format=application/json" \
        + "&monitorType=2" \
        + "&verbose=0" \
        + "&includeconcentrations=0" \
        + "&api_key={api_key}"

    # https://www.airnowapi.org/aq/observation/latLong/current/
    _airnow_radius_endpoint = "?format=application/json" \
        + "&latitude={lat}" \
        + "&longitude={lon}" \
        + "&distance={radius_miles}" \
        + "&API_KEY={key}"

    _wfigs_current_incidents_endpoint = "WFIGS_Interagency_" \
        + "Perimeters_Current/" \
        + "FeatureServer/0/query?f=json&where=" \
        + "(attr_POOState%20IN%20('US-CA'))&outFields=*"

    _wfigs_test_incidents_endpoint = "WFIGS_Interagency_Perimeters/" \
        + "FeatureServer" \
        + "/0/query?f=json&where=" \
        + "(poly_CreateDate%20%3E%3D%" \
        + "20DATE%20'{}'%20" \
        + "AND" \
        + "%20poly_CreateDate%20%3C%3D%" \
        + "20DATE%20'{}')%20" \
        + "AND" \
        + "%20(attr_POOState" \
        + "%20IN%20('US-CA'))&outFields=*"

    _wfigs_latest_incidents_endpoint = "WFIGS_Incident_" \
        + "Locations_Current" \
        + "/FeatureServer/0/" \
        + "query?f=json&" \
        + "where=(POOState%20IN%20('US-CA'))&outFields=*"

    _mapshare_feed_endpoint = "{user}?imei={imei}"

    _send_message_endpoint = "{user}/Map/SendMessageToDevices"
