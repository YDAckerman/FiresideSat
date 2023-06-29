import base64
from helpers.endpoint_templates import MAPSHARE_FEED_ENDPOINT, \
    AIRNOW_RADIUS_ENDPOINT, SEND_MESSAGE_ENDPOINT, \
    WFIGS_TEST_INCIDENT_PERIMETERS_ENDPOINT, \
    WFIGS_TEST_INCIDENT_LOCATIONS_ENPOINT, \
    WFIGS_CURRENT_INCIDENT_PERIMETERS_ENDPOINT, \
    WFIGS_CURRENT_INCIDENT_LOCATIONS_ENDPOINT


def make_headers(usr, pw):
    usr_pw = f'{usr}:{pw}'
    b64_val = base64.b64encode(usr_pw.encode()).decode()
    return {"Authorization": "Basic %s" % b64_val}


class Endpoint():

    def __init__(self, endpoint_template, endpoint_name):
        self.template = endpoint_template
        self.name = endpoint_name

    def format(self, **kwargs):
        return self.template.format(**kwargs)

    def warn(self):
        return "No response from {} endpoint".format(self.name)


class EndpointFactory():

    # https://www.airnowapi.org/aq/observation/latLong/current/

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
