""" Unit test for job posting preprocessor """
import unittest
import requests
import json
from skilloracle import SkillOracle
from contextlib import closing
import psutil
import socket
import subprocess
import shlex

class TestSkillOracle(unittest.TestCase):
    """ Unit test for job preprocessor """

    def setUp(self, port=7000, host='127.0.0.1'):
        self.port = port
        self.host = host

    def netcat(host, port, content):

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, int(port)))
	s.sendall(content.encode())
	s.shutdown(socket.SHUT_WR)
	while True:
	    data = s.recv(4096)
	    if not data:
		break
	    print(repr(data))
	s.close()

    def teardown_all(self, name='vw'):
        """
        Teardown all oracles
        todo: maybe better return code checking?
        """
        ret = subprocess(shlex("killall vw"))
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
        # TODO: Comment this out
        assert True == oracle.check_socket(host=self.host, port=self.port),\
            "Daemon failed to stand up on that host ({}), port ({})".format(self.host, self.port)

        # TODO: new check, by successfully tearing down the oracle we confirm that
        # a) it started up and b) it was killed
        # So, all we need to do is remove the assert True above and proceed directly with the below

        # Cool, we stood up the daemon, now we kill it
        # TODO: Since we directly and test for successfully, tear down the oracle it
        # must have existsed. Finally the daemon check above is another check that it
        # was spawned.
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
