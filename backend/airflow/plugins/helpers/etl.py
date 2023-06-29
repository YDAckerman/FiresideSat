from helpers.endpoint import EndpointFactory


class ELT():

    def __init__(self, endpoint_abbr, load_fun):
        self.endpoint = EndpointFactory().get_endpoint(endpoint_abbr)
        self.load = load_fun

    def run(self, http_hook, pg_hook, context, log):

        pass

## add variables to context



class EtlFunctions():


    def load_from_endpoint(self, endpoint, http_hook, pg_hook, context, log):

        pg_conn = pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        if endpoint == "wildfire_current_endpoint":

            endpoint = self.api \
                           .format_endpoint("wildfire_current_endpoint",
                                            context)

            self._load_from_wildfire_endpoint(http_hook, endpoint,
                                              pg_conn, pg_cur,
                                              context, log)

        elif endpoint == "wildfire_test_endpoint":

            endpoint = self.api \
                           .format_endpoint("wildfire_test_endpoint",
                                            context)

            self._load_from_wildfire_endpoint(http_hook, endpoint,
                                              pg_conn, pg_cur,
                                              context, log)

        elif endpoint == "airnow_endpoint":

            self._load_from_airnow_endpoint(http_hook, pg_conn,
                                            pg_cur, context, log)

        elif endpoint == "mapshare_feed_endpoint":

            self._load_from_mapshare_endpoint(http_hook,
                                              pg_conn, pg_cur,
                                              context, log)
        else:

            raise ValueError("Unrecognized enpoint")

        pg_conn.close()
