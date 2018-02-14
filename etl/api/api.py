""" Skill Labeller DB API """

import falcon
from endpoint import SkillCandidateEndpoint

app = falcon.API()
endpoint = SkillCandidateEndpoint()

app.add_route('/', endpoint)
