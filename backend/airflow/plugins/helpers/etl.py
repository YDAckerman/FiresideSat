from helpers.endpoint import Endpoint
from helpers.elt_process_pairs import PROCESS_DICT as PAIRS


class ELTProcess():

    def __init__(self, endpoint_name, http_hook, pg_hook, context, log):

        pair = PAIRS[endpoint_name]
        self.endpoint = Endpoint(http_hook, endpoint_name, pair['template'])
        self.pg_conn = pg_hook.get_conn()
        self.pg_cur = self.pg_conn.cursor()
        self.context = context
        self.log = log
        self.elt_fun = pair['elt_fun']

    def run(self):

        self.elt_fun(self.endpoint, self.pg_conn,
                     self.pg_cur, self.context,
                     self.log)

        self.pg_conn.close()
