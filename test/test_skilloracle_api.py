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
        yml_path = ""

        if not service:
            service = ""

        if not cmd:
            cmd = ""

        if yml:
            yml_path = os.path.join(os.path.dirname(__file__),
                                    path,
                                    yml)
            yml_path = "-f " + yml_path
        else:
            yml = ""

        # see: https://stackoverflow.com/a/34459371/3662899,
        # want to deattach from the Python process to reflect how a standalone API
        # would really behave under docker calls, containers
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
        self.port = "8080" # todo: extract from docker-compose.yml instead

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
        """

        """
        assert self.dockercompose.run(cmd='up'), "Was not able to run docker-compose up"

        time.sleep(5) # wait for containers to stand up

        service_ip = self.dockercompose.extract_service_ip()

        assert len(service_ip.split('.')) == 4, "Service ip is malformed!"

    def test_put_api(self):
        assert self.dockercompose.run(cmd='up'), "Was not able to run docker-compose up"
        time.sleep(5) # wait for containers to stand up
        service_ip = self.dockercompose.extract_service_ip()
        assert len(service_ip.split('.')) == 4, "Service ip is malformed!"

        # test PUT with known label
        data = {'context': 'I like for pleasure!', 'label': '-1', 'name': 'reading books'}
        response = requests.put("http://"+service_ip+":"+self.port, params=data)
        assert response.status_code == 200,\
                "API response was non-200 ({}) for labelled PUT call".format(response.status_code)

        # test PUT with no label (adding to candidate queue)
        data = {'context': 'I like for pleasure!', 'label': None, 'name': 'reading books'}
        response = requests.put("http://"+service_ip+":"+self.port, params=data)
        assert response.status_code == 200,\
                "API response was non-200 ({}) for no label PUT call".format(response.status_code)

        keys = json.loads(response.text).keys()

        assert "prediction" in keys and\
               "importance" in keys, "API response did not have prediction, importance keys!"
        # actual values don't really matter, typically are 0, 0

    def test_get_api(self):
        assert self.dockercompose.run(cmd='up'), "Was not able to run docker-compose up"
        time.sleep(5) # wait for containers to stand up
        service_ip = self.dockercompose.extract_service_ip()
        assert len(service_ip.split('.')) == 4, "Service ip is malformed!"

        # PUT one candidate skill
        data = {'context': 'I like for pleasure!', 'label': None, 'name': 'reading books'}
        response = requests.put("http://"+service_ip+":"+self.port, params=data)
        assert response.status_code == 200,\
                "API response was non-200 ({}) for labelled PUT call".format(response.status_code)

        # GET a candidate skill
        response = requests.get("http://"+service_ip+":"+self.port)
        assert response.status_code == 200,\
                "API response was non-200 ({}) for GET call".format(response.status_code)

    def teardown(self):
        # Note: this seems to take an oddly long time to complete
        # I wonder if the pytest exiting kills the docker-compose down command, although
        # I thought it was spawned as a seperate process..
        #
        # Note:
        # This causes some side effects since it takes so long to complete int hat multiple runs of this
        # unit test can interact w another, causing a test expecting a service to be up to
        # have no service up when a docker-compose up instantly passes and the docker-compose down
        # finally kicks in from an older test. Beware!
        assert self.dockercompose.run(cmd='down', service=None, yml=None), "Was not able to run docker-compose down"
