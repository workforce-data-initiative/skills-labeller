""" Skill Labeller Preprocessor API endpoint """
import json
import falcon
from utils.mongo import MongoDatabase


class SkillCandidateEndpoint(object):
    def __init__(self):
        self.db = MongoDatabase()

    def on_get(self, req, resp):
        resp.body = json.dumps(self.db.sample_candidate())
        resp.status = falcon.HTTP_200
