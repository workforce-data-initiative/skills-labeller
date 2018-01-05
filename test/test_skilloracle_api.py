""" Unit test for skill oracle API"""
import time
import unittest
import requests
import json

class TestSkillOracleAPI(unittest.TestCase):
    """ Unit test for Skill Oracle API """

    def setUp(self, port=7000, host='127.0.0.1'):
        self.port = port
        self.host = host
        self.redis = "redis"

        # todo:
        # check that docker-compose exists, is of right version

    def test_mytest(self):

        return True
