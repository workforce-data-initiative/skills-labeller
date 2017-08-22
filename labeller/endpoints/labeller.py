""" Skill Labeller API endpoints. """
import json
import falcon
import random

try:
    from labeller import MongoDatabase
except:
    from ..db.mongo import MongoDatabase


class LabellerEndpoint(object):
    def __init__(self):
        self.db = MongoDatabase()
        self.valid_keys = ['title', 'responsibilities', 'qualifications',
                           'experienceRequirements', 'skills',
                           'jobDescription', 'educationRequirements']

    def on_get(self, req, resp):
        sample = self.db.get_random_posting()
        found_data = False
        while not found_data:
            selected_key = random.randint(0, len(self.valid_keys) - 1)
            data = sample[self.valid_keys[selected_key]]
            if len(data) > 0:
                found_data = True

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'skill_candidate': data})

    def on_post(self, req, resp):
        pass
