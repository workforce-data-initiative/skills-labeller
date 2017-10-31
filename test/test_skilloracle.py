""" Unit test for job posting preprocessor """
import unittest
import requests
import json
from skilloracle import SkillOracle
import subprocess
import shlex

class TestSkillOracle(unittest.TestCase):
    """ Unit test for job preprocessor """

    def setUp(self, port=7000, host='127.0.0.1'):
        self.port = port
        self.host = host

    def teardown_all(self, name='vw'):
        """
        Teardown all oracles
        todo: maybe better return code checking?
        """
        ret = subprocess.call(shlex.split('killall vw'))
        return ret == 0

    def standup_new_oracle(self, host=None, port=None):
        oracle = None

        # Shutdown any instances of the oracle for clean testing
        ret = self.teardown_all()
        assert True == ret or False == ret, "Could not shutdown existing/non existing oracle instances"

        # Now stand up an oracle on the given port. host is None, defaults to local host
        oracle = SkillOracle(port=self.port) # stands up a daemon
        return oracle

    def teardown_oracle(self, oracle=None):
        """
        Teardown an instance of an oracle by call its .kill() function.
        """
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

    def test_PUT(self):
        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        oracle.PUT(label="1",
                   name="ability to accept and learn from criticism",
                   context="furthermore, some accomplishments that I\
                            have gained is having the and always have\
                            a positive attitude.")

        self.teardown_oracle(oracle=oracle)
