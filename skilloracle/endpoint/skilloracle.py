""" Skill Labeller Preprocessor API endpoint """
import json
import falcon
import random
import logging

## This default skill oracle needs no imports but yours might
#try:
#    from preprocessor import DefaultSingleRank
#except:
#    from ..preprocesser.singlerank import DefaultSingleRank

class SkillOracleEndpoint(object):
    def __init__(self):
        self.preprocessor = {'default': DefaultSingleRank()}
        self.valid_keys = {'job_posting', 'n_keyterms'}
        self.preprocessors = set(self.preprocessor.keys())

    def on_get(self, req, resp):
        keyphrases = None

        # how do we santize this? What do we santize? Job postings can have anything
        query = falcon.uri.parse_query_string(req.query_string) # I assume this de-urlencodes
        query_keys = set(query.keys())

        # ensure that users are respecting the api, sending nothing beyond the valid keys
        if set(self.valid_keys).issuperset(query_keys):

            text = query['job_posting']
            n_keyterms = None
            if 'n_keyterms' in query['n_keyterms']:
                n_keyterms = query['n_keyterms']

            keyphrases = {}
            for name in self.preprocessors:
                keyphrases[name] =\
                        self.preprocessor[name].\
                                get_job_posting_keyterms(text=text, n_keyterms=n_keyterms)

            resp.status = falcon.HTTP_200

        resp.body = json.dumps({'preprocesser': {'potential_skills': keyphrases}})

    def on_post(self, req, resp):
        pass
