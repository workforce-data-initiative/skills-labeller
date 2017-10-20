""" Unit test for job posting preprocessor """
import unittest
import requests
import json

class TestJobProcessingPreprocessor(unittest.TestCase):
    """ Unit test for job preprocessor """

    def setUp(self, port=3000, host='localhost'):
        self.port = port
        self.host = host

    def test_preprocessor(self):
        success = "fox fox fox"

        text = "fox fox fox multi tool jumped over the fence and and"
        n_keyterms = 0.05

        payload = {'job_posting':text, 'n_keyterms':n_keyterms}
        url = "http://{host}:{port}".format(host=self.host, port=self.port)

        r = requests.get(url, params=payload)
        potential = json.loads(r.text)['preprocesser']['potential_skills']['default']
        self.assertTrue(len(potential) > 0)
        self.assertTrue(potential[0] == success)
