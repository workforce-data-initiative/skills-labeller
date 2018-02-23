""" Unit test for candidate skill selector"""
import unittest
import requests
import json
from etl.utils.mongo import MongoDatabase


class TestCandidateSkillSelector(unittest.TestCase):
    """ Unit test for candidate skill selector"""

    def setUp(self, port=3001, host='localhost'):
        self.port = port
        self.host = host

    def test_get_random_candidate(self):
        url = "http://{host}:{port}".format(host=self.host, port=self.port)
        r = requests.get(url)
        random_candidate = json.loads(r.text)
        assert 'context' in random_candidate
        assert 'token' in random_candidate
        assert 'expected_label' in random_candidate
        assert 'preprocessor_id' in random_candidate
