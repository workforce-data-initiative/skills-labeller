""" Unit test for skill oracle API"""
import time
import unittest
import requests
import json
import os
import subprocess
import shlex

class DockerCompose(object):
    """
    Helper class for interacting with DockerCompose via subprocess
    """
    def __init__(self):
        self.program = 'docker-compose'
        self.version_string = '--version'
        self.up = 'up'

    def get_version(self):
        try:
            ret = subprocess.check_output([self.program, self.version_string],
                                          stderr=subprocess.STDOUT)
        except OSError:
            raise OSError("docker-compose must be installed!") from OSError

        # get the version number, assuming the following format ... ... version, ...
        ret = ret.decode("utf").split()[2][:-1]

        return ret

    def run(self, path="../", yml="docker-compose.yml", service="skilloracle", cmd=None):
        if yml:
            yml_path = os.path.join(os.path.dirname(__file__),
                                    path,
                                    yml)
            yml_path = "-f " + yml_path
        # see: https://stackoverflow.com/a/34459371/3662899,
        # want to deattach from the Python process to reflect how a standalone API
        # would really behave

        shell_command = " ".join([self.program, yml_path, cmd, service])
        ret = subprocess.Popen(shell_command,
                               shell=True,
                               close_fds=True)

        return ret._child_created

    def extract_service_ip(self, service="skilloracle"):
        ret = None
        shell_command = "docker inspect -f '{{.Name}}"           +\
                        "- {{range .NetworkSettings.Networks}}"  +\
                        " {{.IPAddress}}{{end}}' $(docker ps -q)"

        ips = subprocess.check_output(shell_command, shell=True)

        for line in ips.decode('utf-8')[:-1].split('\n'):
            service_line = line.split('-')
            if service in service_line[0]:
                ret = service_line[1].strip()
                break

        return ret

class TestSkillOracleAPI(unittest.TestCase):
    """ Unit test for Skill Oracle API """

    def setUp(self):
        self.dockercompose = DockerCompose()

    def test_check_version(self):
        """
        This is a very basic version check and isn't robust against
        letters and other ways of indicating versions. There are python
        libraries offering better version testing to consider using.
        """
        ret = self.dockercompose.get_version()
        split_version = ret.split('.')
        assert int(split_version[0]) >= 1,\
            "Major Docker-compose version is too low ({})".format(split_version[0])

        assert int(split_version[1]) >= 10,\
            "Minor Docker-compose version is too low ({})".format(split_version[1])

    def test_up(self):
        assert self.dockercompose.run(cmd='up'), "Was not able to run docker-compose up"

        service_ip = self.dockercompose.extract_service_ip()

        assert len(service_ip.split('.')) == 4, "Service ip is malformed!"
