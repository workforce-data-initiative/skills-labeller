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
        self.put_valid_keys = { 'name', 'context', 'label'}
        self.fetcher = fetcher
        if not fetcher:
            fetcher = None # what kind of default woudl we do here?

    def on_put(self, req, resp):
        query = falcon.uri.parse_query_string(req.query_string)
        # ^ just use req.params.items or, below, req.params.keys()
        query_keys = set(query.keys())

        #if self.put_valid_keys.issuperset(query_keys):
        if query_keys.issubset(self.put_valid_keys):
            label = query['label']\
                    if 'label' in query else None
            name = query['name']\
                    if 'name' in query else None
            context = query['context']\
                    if 'context' in query else None

            response = self.oracle.PUT(label=label,
                                       name=name,
                                       context=context)

            resp.body = json.dumps(response) # should this versioned?

            resp.status = falcon.HTTP_200

    def on_get(self, req, resp):
        response = self.oracle.GET()
        response["response"] = json.loads(response["response"])

        print(response)

        # Note tested to date, need to resolve fetcher/db access
        name = response['response']['name']
        context = response['response']['context']
        importance = response['importance']
        number = response['number of candidates']

        resp.body = json.dumps({'name':name,
                                'context':context,
                                'importance':importance,
                                'number of candidates': number})

        resp.status = falcon.HTTP_200
