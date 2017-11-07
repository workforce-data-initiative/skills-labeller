""" Unit test for job posting preprocessor """
import unittest
import requests
import json
from skilloracle import SkillOracle
import subprocess
import shlex
import redis

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

    @unittest.skip('Skip create, destroy...')
    def test_create_and_destroy_oracle(self):
        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        # Verify that something was stood up on the port
        assert True == oracle.check_socket(host=self.host, port=self.port),\
            "Daemon failed to stand up on that host ({}), port ({})".format(self.host, self.port)

        # Cool, we stood up the oracle, now we kill it
        ret = self.teardown_oracle(oracle=oracle)
        assert True == ret, "Failed to kill skill oracle!"

    @unittest.skip('Skip PUT...')
    def test_PUT(self):
        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        oracle.PUT(label="1",
                   name="ability to accept and learn from criticism",
                   context="furthermore, some accomplishments that I\
                            have gained is having the and always have\
                            a positive attitude.")

        self.teardown_oracle(oracle=oracle)

    # This section tests GET related functionality
    # Assumes that an instance of Redis is accessible via local host, on the default port
    def test_GET(self, encoding="utf-8"):
        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        # note: we use a string as a key but in production keys are likely to be
        # skill ids
        encoding=encoding
        key = "ability to accept and learn from criticism"
        importance = 1.23

        redis_db = redis.StrictRedis()# defaults to 127.0.0.1:6379, db=SKILL_CANDIDATES
        redis_db.zadd(oracle.SKILL_CANDIDATES,
                      importance,
                      key)

        response, num_popped = oracle.GET() # assumes Redis on localhost, default port
        key_with_score = response[0]

        assert key == key_with_score[0].decode(encoding), 'Oracle GET did not return added key'
        assert importance == key_with_score[1], 'Oracle GET did not return added score'
        assert num_popped == 1, 'Oracle GET did not return expected number items popped (1)'

        self.teardown_oracle(oracle=oracle)
