""" Unit test for skill oracle """
import time
import unittest
import requests
import json
from skilloracle.skilloracle import SkillOracle
import subprocess
import shlex
import redis

class TestSkillOracle(unittest.TestCase):
    """ Unit test for job preprocessor """

    def setUp(self, port=7000, host='127.0.0.1'):
        self.port = port
        self.host = host
        self.redis = "redis"

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
        oracle = SkillOracle(host='127.0.0.1',
                             port=self.port) # stands up a daemon
        return oracle

    def teardown_oracle(self, oracle=None):
        """
        Teardown an instance of an oracle by call its .kill() function.
        """
        ret = oracle.kill()
        return ret

    #@unittest.skip('Skip create, destroy...')
    def test_create_and_destroy_oracle(self):
        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        # Verify that something was stood up on the port
        assert True == oracle.check_socket(host=self.host, port=self.port),\
            "Daemon failed to stand up on that host ({}), port ({})".format(self.host, self.port)

        # Cool, we stood up the oracle, now we kill it
        ret = self.teardown_oracle(oracle=oracle)
        assert True == ret, "Failed to kill skill oracle!"

    #@unittest.skip('Skip PUT...')
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
        # skill ids, that are given to the UI for fetching (?)
        encoding=encoding
        key = "ability to accept and learn from criticism" # todo: encode w encoding?
        importance = 1.23

        # Set up redis with one candidate, flush all others
        redis_db = redis.StrictRedis(self.redis)# defaults to redis:6379
        redis_db.flushall() # clean slate
        redis_db.zadd(oracle.SKILL_CANDIDATES,
                      importance,
                      key)

        response, _, size = oracle.GET()
        key_with_score = response[0]

        assert key == key_with_score[0].decode(encoding), 'Oracle GET did not return added key'
        assert importance == key_with_score[1], 'Oracle GET did not return added score/importance'
        assert size == 0, 'Oracle GET did not return expected number items (0)'

        redis_db.flushall() # clean the slate
        # redis_db.shutdown() # can't really do this since we didn't start it up
        self.teardown_oracle(oracle=oracle)

    def test_fetch_push_more(self):
        # could be a database connection that yields candidates
        fetcher = [
                    {'name': "ability to accept and learn from criticism",
                     'context': "furthermore, some accomplishments that I\
                    have gained is having the and always have\
                     a positive attitude."},\
                    {'name': "reading",
                     'context': "desired candidate will be for many hours a day."}
                  ]
        expected_size = len(fetcher)

        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        # Set up redis with one candidate, flush all others
        redis_db = redis.StrictRedis(self.redis)# defaults to redis:6379
        redis_db.flushall() # clean slate

        oracle.fetch_push_more(fetcher=fetcher)

        size = redis_db.zcard(oracle.SKILL_CANDIDATES)

        assert expected_size == size, "Was not able to push expected number of fetch_push_more\
                                            items onto candidate data store!"

        # Shutdown candidate store
        redis_db.flushall() # clean the slate
        self.teardown_oracle(oracle=oracle)

    def test_push_once(self):
        # could be a database connection that yields candidates
        fetcher = [
                    {'name': "ability to accept and learn from criticism",
                     'context': "furthermore, some accomplishments that I\
                    have gained is having the and always have\
                     a positive attitude."},\
                    {'name': "reading",
                     'context': "desired candidate will be for many hours a day."}
                  ]
        expected_size = len(fetcher)

        oracle = self.standup_new_oracle(port=self.port)
        assert None != oracle, "Failed to create oracle."

        # Set up redis with one candidate, flush all others
        redis_db = redis.StrictRedis(self.redis)# defaults to redis:6379
        redis_db.flushall() # clean slate, size is zero

        # so we start w an empty candidate store, and we push stuff onto it with a
        # a really long period ...
        threshold = 1
        period = 60*2 # 2 minutes, very long for this test

        start = time.time()
        oracle._push_once(size=0, threshold=threshold, fetcher=fetcher, period=period)

        stop = time.time()

        assert stop-start < period, "Took longer than period time to call `_push_once`! Can't run test."

        # Test sequential push, within time period
        oracle._push_once(size=0, threshold=threshold, fetcher=fetcher, period=period)
        stop2 = time.time()

        # Check that we attempt to push twice w/in the period of time given, testing that only
        # one push makes it though...
        assert stop2-start < period, "Took longer than period time to call second `_push_once`! Can't run test."

        # So, we tried to push twice within the period window, but the candidate
        # store should the same as expected size, not 2* expected size

        size = redis_db.zcard(oracle.SKILL_CANDIDATES)

        assert expected_size == size, "Did not push expected number of\
                                       items items onto candidate data\
                                       store ({num})!".format(num=size)

        # Shutdown candidate store
        redis_db.flushall() # clean the slate
        self.teardown_oracle(oracle=oracle)
