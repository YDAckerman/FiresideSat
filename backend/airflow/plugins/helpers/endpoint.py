from airflow.models import Variable
import base64


def make_headers(usr, pw):
    usr_pw = f'{usr}:{pw}'
    b64_val = base64.b64encode(usr_pw.encode()).decode()
    return {"Authorization": "Basic %s" % b64_val}


class Endpoint():

    def __init__(self, endpoint_template):
        self.template = endpoint_template

    def format(self, **kwargs):
        return self.template.format(**kwargs)


class EndpointFactory():

    # https://www.airnowapi.org/aq/observation/latLong/current/
    AIRNOW_RADIUS_ENDPOINT = "?format=application/json" \
        + "&latitude={lat}" \
        + "&longitude={lon}" \
        + "&distance={radius_miles}" \
        + "&API_KEY={key}"

    WFIGS_CURRENT_INCIDENT_PERIMETERS_ENDPOINT = "WFIGS_Interagency_" \
        + "Perimeters_Current/" \
        + "FeatureServer/0/query?f=json&where=" \
        + "(attr_POOState%20IN%20('US-CA'))&outFields=*"

    WFIGS_CURRENT_INCIDENT_LOCATIONS_ENDPOINT = "WFIGS_Incident_" \
        + "Locations_Current" \
        + "/FeatureServer/0/" \
        + "query?f=json&" \
        + "where=(POOState%20IN%20('US-CA'))&outFields=*"

    WFIGS_TEST_INCIDENT_LOCATIONS_ENPOINT = "WFIGS_Incident_Locations" \
        + "/FeatureServer/0/" \
        + "query?f=json&where=" \
        + "(FireDiscoveryDateTime%20%3E%3D%20DATE%20'{start_date}'%20" \
        + "AND" \
        + "%20FireDiscoveryDateTime%20%3C%3D%20DATE%20'{end_date}')%20" \
        + "AND" \
        + "%20(POOState%20IN%20('US-CA'))" \
        + "&outFields=*"

    WFIGS_TEST_INCIDENT_PERIMETERS_ENDPOINT = "WFIGS"\
        + "_Interagency_Perimeters/" \
        + "FeatureServer" \
        + "/0/query?f=json&where=" \
        + "(poly_CreateDate%20%3E%3D%" \
        + "20DATE%20'{start_date}'%20" \
        + "AND" \
        + "%20poly_CreateDate%20%3C%3D%" \
        + "20DATE%20'{end_date}')%20" \
        + "AND" \
        + "%20(attr_POOState" \
        + "%20IN%20('US-CA'))&outFields=*"

    MAPSHARE_FEED_ENDPOINT = "{user}?imei={imei}"

    SEND_MESSAGE_ENDPOINT = "{user}/Map/SendMessageToDevices"

    endpoint_dict = {
        'mapshare': MAPSHARE_FEED_ENDPOINT,
        'airnow': AIRNOW_RADIUS_ENDPOINT,
        'send_message': SEND_MESSAGE_ENDPOINT,
        'test_perimeters': WFIGS_TEST_INCIDENT_PERIMETERS_ENDPOINT,
        'test_locations': WFIGS_TEST_INCIDENT_LOCATIONS_ENPOINT,
        'current_perimeters': WFIGS_CURRENT_INCIDENT_PERIMETERS_ENDPOINT,
        'current_locations': WFIGS_CURRENT_INCIDENT_LOCATIONS_ENDPOINT
    }

    def get_endpoint(self, endpoint_abbr):
        return Endpoint(self.endpoint_dict[endpoint_abbr])
