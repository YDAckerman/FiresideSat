from helpers.endpoint import Endpoint
from helpers.elt_funs import elt_wildfire_locations, \
    elt_wildfire_perimeters, \
    elt_mapshare_locs, \
    elt_fire_locs_aqi

ELT_DICT = {
        'mapshare': elt_mapshare_locs,
        'airnow': elt_fire_locs_aqi,
        'test_perimeters': elt_wildfire_perimeters,
        'test_locations': elt_wildfire_locations,
        'current_perimeters': elt_wildfire_perimeters,
        'current_locations': elt_wildfire_locations,
}


class ELTProcess():

    def __init__(self, endpoint_name, http_hook, pg_hook, context, log):
        self.endpoint = Endpoint(http_hook, endpoint_name)
        self.pg_conn = pg_hook.get_conn()
        self.pg_cur = self.pg_conn.cursor()
        self.context = context
        self.log = log
        self.elt_fun = ELT_DICT[self.endpoint.name]

    def run(self):

        self.elt_fun(self.endpoint, self.pg_conn,
                     self.pg_cur, self.context,
                     self.log)

        self.pg_conn.close()
