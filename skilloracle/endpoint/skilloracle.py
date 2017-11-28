""" Skill Labeller Preprocessor API endpoint """
import json
import falcon
import random
import logging

try:
    from skilloracle import SkillOracle
except:
    from ..skilloracle import SkillOracle


# This endpoint is WIP
class SkillOracleEndpoint(object):
    def __init__(self, fetcher=None):
        self.oracle = SkillOracle(port=7000)
        self.put_valid_keys = {'label', 'name', 'context'}
        self.fetcher = fetcher
        if not fetcher:
            fetcher = None # what kind of default woudl we do here?

    def on_put(self, req, resp):
        query = falcon.uri.parse_query_string(req.query_string)
        query_keys = set(query.keys())

        if self.put_valid_keys.issuperset(query_keys):
            label = query['label']
            name = query['name']
            context = query['context']

            response = self.oracle.PUT(label=label,
                                       name=name,
                                       context=context)

            resp.body = json.dumps(response) # should this versioned?

            resp.status = falcon.HTTP_200

    def on_get(self, req, resp):
        response = self.oracle.GET()
        self.oracle.fetch_push_more(fetcher=self.fetcher)

        # Note tested to date, need to resolve fetcher/db access
        candidate = response['candidate skill']
        context = response['']# todo: fix __fetch_push_more to also push the context
        importance = response[2]

        resp.body = json.dumps({'skilloracle' :\
                                    {'cadidate':candidate,
                                     'context':context,
                                     'importance':importance} })

        resp.status = falcon.HTTP_200
