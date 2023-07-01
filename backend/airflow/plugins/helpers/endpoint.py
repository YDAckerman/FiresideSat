

class Endpoint():

    def __init__(self, http_hook, endpoint_name, template):
        self._http_hook = http_hook
        self._template = template
        self._name = endpoint_name

    @property
    def name(self):
        return self._name

    def set_route(self, *args, **kwargs):
        self.route = self._template.format(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._http_hook.run(endpoint=self.route,
                                   *args, **kwargs)

    def post(self, json=None, *args, **kwargs):
        if not json:
            raise ValueError("must provide data to post")
        return self._http_hook.run(endpoint=self.route,
                                   json=json,
                                   *args, **kwargs)

    def warn(self):
        return "No response from {} endpoint".format(self._name)
