""" Skill Labeller Preprocessor API endpoint """
import json
import falcon
import random
import logging

try:
    from skilloracle import SkillOracle
except:
    from ..skilloracle import SkillOracle

class SkillOracleEndpoint(object):
    def __init__(self, fetcher=None):
        self.host = "skilloracle"
        self.oracle = SkillOracle(host=self.host, port=7000)
        self.put_valid_keys = {'label', 'name', 'context'}
        self.fetcher = fetcher
        if not fetcher:
            fetcher = None # what kind of default woudl we do here?

    def on_put(self, req, resp):
        query = falcon.uri.parse_query_string(req.query_string)
        # ^ just use req.params.items or, below, req.params.keys()
        query_keys = set(query.keys())

        if self.put_valid_keys.issuperset(query_keys):
            print(req.params)
            label = ''
            name = ''
            context = ''

            if 'label' in req.params:
                label = req.params['label'][0] # [0] if multiple values?
            if 'name' in req.params:
                name = req.params['name'][0]
            if 'context' in req.params:
                context = req.params['context'][0]

            response = self.oracle.PUT(label=label,
                                       name=name,
                                       context=context)

            resp.body = json.dumps(response) # should this versioned?

            resp.status = falcon.HTTP_200

    def on_get(self, req, resp):
        response = self.oracle.GET()

        # Note tested to date, need to resolve fetcher/db access
        candidate = response['candidate skill']
        importance = response['importance']
        number = response['number of candidates']
        context = " " # TODO: put context in json obj on_Put, extract on_get

        resp.body = json.dumps({'skilloracle' :\
                                    {'candidate':candidate,
                                     'context':context,
                                     'importance':importance,
                                     'number of candidates': number} })

        resp.status = falcon.HTTP_200
