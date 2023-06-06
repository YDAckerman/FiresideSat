from airflow.models import Variable


class ApiEndpoint():

    def __init__(self):
        print("using api endpoint")

    def format_endpoint(self, endpoint_name, context=None):

        if endpoint_name == "wildfire_endpoint":

            if context is None:
                raise ValueError("This endpoint requires context data")
            else:
                return self._format_wildfire_endpoint(context)

        elif endpoint_name == "airnow_endpoint":

            if context is None:
                raise ValueError("This endpoint requires context data")
            else:

                api_key = Variable.get("airnow_api_key")
                return self._format_airnow_endpoint(context.get('lat'),
                                                    context.get('lon'),
                                                    api_key)

        elif endpoint_name == "mapshare_feed_endpoint":

            if context is None:
                raise ValueError("This endpoint requires context data")
            else:
                return self._mapshare_feed_endpoint \
                           .format(user=context.get("mapshare_id"),
                                   imei=context.get("garmin_imei"))

        elif endpoint_name == "send_message_endpoint":

            if context is None:
                raise ValueError("This endpoint requires context data")
            else:
                return self._send_message_endpoint \
                           .format(user=context.get("mapshare_id"))

        else:

            raise ValueError("Unrecognized enpoint")

    def _format_airnow_endpoint(self, lat, lon, api_key):

        return self \
            ._airnow_radius_endpoint \
            .format(lat=lat, lon=lon, key=api_key)

    def _format_wildfire_endpoint(self, context):

        current_date = context.get('data_interval_start')
        start_date = current_date.to_date_string()
        end_date = current_date \
            .add(days=1) \
            .to_date_string()

        return self._wildfire_incidents_test_endpoint \
                   .format(start_date, end_date)

    _airnow_bbox_url = "https://airnowapi.org/aq/data/" \
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
        + "&distance=150" \
        + "&API_KEY={key}"

    _active_wildfire_incidents_url = "https://services3.arcgis.com/" \
        + "T4QMspbfLg3qTGWY/arcgis/rest/services/" \
        + "Current_WildlandFire_Perimeters/" \
        + "FeatureServer/0/query?f=json&where=" \
        + "(irwin_POOState%20IN%20(%27US-CA%27))&outFields=*"

    _wildfire_incidents_test_url = "https://services3.arcgis.com/" \
        + "T4QMspbfLg3qTGWY/arcgis" \
        + "/rest/services/" \
        + "WFIGS_Interagency_Perimeters/" \
        + "FeatureServer" \
        + "/0/query?f=json&where=" \
        + "(poly_CreateDate%20%3E%3D%" \
        + "20DATE%20'{}'%20" \
        + "AND" \
        + "%20poly_CreateDate%20%3C%3D%" \
        + "20DATE%20'{}')%20" \
        + "AND" \
        + "%20(irwin_POOState" \
        + "%20IN%20('US-CA'))&ouFields=*"

    _wildfire_incidents_test_endpoint = "WFIGS_Interagency_Perimeters/" \
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

    _mapshare_feed_endpoint = "{user}?imei={imei}"

    _send_message_endpoint = "{user}/Map/SendMessageToDevices"
