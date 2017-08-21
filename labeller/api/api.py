""" Skill Labeller API """

import falcon
from ..endpoints.labeller import LabellerEndpoint

app = falcon.API()
labeller = LabellerEndpoint()

app.add_route('/', labeller)
