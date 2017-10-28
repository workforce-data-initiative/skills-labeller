""" Unit test for job posting preprocessor """
import unittest
import requests
import json
from skilloracle import SkillOracle
from contextlib import closing
import psutil
import socket


class TestSkillOracle(unittest.TestCase):
    """ Unit test for job preprocessor """

    def setUp(self, port=7000, host='127.0.0.1'):
        self.port = port
        self.host = host

    def test_create_and_destroy_daemon(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            daemon_exists= sock.connect_ex((self.host, self.port)) == 0

        assert False == daemon_exists,\
            "Daemon already exists on that host ({}), port ({})".format(self.host, self.port)

        oracle = SkillOracle(port=self.port) # stands up a daemon

        assert True == oracle.check_socket(host=self.host, port=self.port),\
            "Daemon failed to stand up on that host ({}), port ({})".format(self.host, self.port)

        # kill daemon, we're done
        assert True == oracle.kill(), "Failed to kill skill oracle!"


    def test_preprocessor(self):
        # todo: remove me
        return True

        success = "fox fox fox"

        text = "fox fox fox multi tool jumped over the fence and and"
        n_keyterms = 0.05

        payload = {'job_posting':text, 'n_keyterms':n_keyterms}
        url = "http://{host}:{port}".format(host=self.host, port=self.port)

        r = requests.get(url, params=payload)
        potential = json.loads(r.text)['preprocesser']['potential_skills']['default']
        self.assertTrue(len(potential) > 0)
        self.assertTrue(potential[0] == success)
