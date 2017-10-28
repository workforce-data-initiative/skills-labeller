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

    def standup_new_oracle(self, host=None, port=None):
        oracle = None

        # Check that nothing is running on our port, need to start w a clean slate
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            daemon_exists= sock.connect_ex((self.host, self.port)) == 0

        assert False == daemon_exists,\
            "Daemon already exists on that host ({}), port ({})".format(self.host, self.port)

        # Now stand up an oracle on the given port. host is None, defaults to local host

        # todo: this involves an interaction between my fork of wabbit wappa and how it handles
        # whether to launch or look for a daemon, might want to tidy up
        oracle = SkillOracle(port=self.port) # stands up a daemon

        return oracle

    def teardown_oracle(self, oracle=None):
        ret = False
        ret = oracle.kill()
        return ret

    def test_create_and_destroy_daemon(self):
        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        # Verify that something was stood up on the port
        assert True == oracle.check_socket(host=self.host, port=self.port),\
            "Daemon failed to stand up on that host ({}), port ({})".format(self.host, self.port)

        # Cool, we stood up the daemon, now we kill it
        ret = self.teardown_oracle(oracle=oracle)
        assert True == ret, "Failed to kill skill oracle!"

    @unittest.skip('Skipping PUT while debugging')
    def test_PUT(self):
        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        oracle.PUT(label="1",
                   name="ability to accept and learn from criticism",
                   context="furthermore, some accomplishments that I\
                            have gained is having the and always have\
                            a positive attitude.")

        self.teardown_oracle(oracle=oracle)
