""" Skill Labeller Preprocessor API endpoint """
import json
import falcon
import random
import logging

try:
    from skilloracle import SkillOracle
except:
    from ..skilloracle.skilloracle import SkillOracle

class SkillOracleEndpoint(object):
    def __init__(self):
        self.oracle = SkillOracle(port=7000)
        self.put_valid_keys = {'label', 'name', 'context'}

    def on_put(self, req, resp):
        query = falcon.uri.parse_query_string(req.query_string)
        query_keys = set(query.keys())

        if self.put_valid_keys.issuperset(query_keys):
            label = query['label']
            name = query['name']
            context = query['context']

            self.oracle.PUT(label, name, context)

            resp.status = falcon.HTTP_200

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
