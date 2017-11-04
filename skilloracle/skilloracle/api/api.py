""" Skill Labeller Preprocessor API """

import falcon
from ..endpoint.skilloracle import SkillOracleEndpoint

app = falcon.API()
endpoint = SkillOracleEndpoint()

app.add_route('/', endpoint)
