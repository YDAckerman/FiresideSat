from helpers.endpoint_templates import ENDPOINT_DICT
import base64


class Endpoint():

    def __init__(self, http_hook, endpoint_name):
        self._http_hook = http_hook
        self._template = ENDPOINT_DICT[endpoint_name]
        self._name = endpoint_name

    @property
    def name(self):
        return self._name

    def _format(self, *args, **kwargs):
        return self._template.format(*args, **kwargs)

    def run(self, context_vars, headers=None):
        return self._http_hook \
                   .run(endpoint=self._format(**context_vars),
                        headers=headers)

    def warn(self):
        return "No response from {} endpoint".format(self._name)

    @staticmethod
    def make_headers(usr, pw):
        usr_pw = f'{usr}:{pw}'
        b64_val = base64.b64encode(usr_pw.encode()).decode()
        return {"Authorization": "Basic %s" % b64_val}
