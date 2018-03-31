""" Unit test for etl API"""
import time
import unittest
import requests
import json
import os
import subprocess
import shlex
try:
    from nameko.standalone.rpc import ClusterRpcProxy
except ImportError:
    raise ImportError("This unittest requires Nameko to be installed. You can install it with `pip install nameko`")

# note: we should really make this part of a utils file in tests :-/
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

class TestETLAPI(unittest.TestCase):
    """ Unit test for ETL API """

    @classmethod
    def setUpClass(cls):
        cls.dockercompose = DockerCompose()
        assert cls.dockercompose.run(cmd='up', service='etl'), "Was not able to run docker-compose up"
        # this should more intelligent, like query service ips, return when a
        # 3 services are up and amqp is responding
        time.sleep(30)

        # Check that key services are up and running
        # should probably pull this name out of a config file as well .. :-/
        cls.rabbit_ip = cls.dockercompose.extract_service_ip('rabbit')
        assert len(cls.rabbit_ip.split('.')) == 4, "Rabbit MQ service ip is malformed/None!"

        service_ip = cls.dockercompose.extract_service_ip('etl') # is this needed?
        assert len(service_ip.split('.')) == 4, "ETL service ip is malformed!"

        # assumes the rabbit mq config hasn't changed, should be read in from a config file :-/
        cls.config = {
            'AMQP_URI': 'amqp://guest:guest@{service_ip}:5672'.format(service_ip=cls.rabbit_ip)
        }

    def test_check_version(self):
        """
        This is a very basic version check and isn't robust against
        letters and other ways of indicating versions. There are python
        libraries offering better version testing to consider using.

        note; this may be redundant with the setUpClass use of of docker
        """
        ret = self.dockercompose.get_version()
        split_version = ret.split('.')
        assert int(split_version[0]) >= 1,\
            "Major Docker-compose version is too low ({})".format(split_version[0])

        assert int(split_version[1]) >= 10,\
            "Minor Docker-compose version is too low ({})".format(split_version[1])

    def test_check_mongo_api(self):
        with ClusterRpcProxy(self.config) as cluster_rpc:
            self.assertTrue(cluster_rpc.ccarsjobsposting_service.check_mongo(),\
                    "RPC etl.vt.check_mongo failed!")

    def test_add_all(self):
        with ClusterRpcProxy(self.config) as cluster_rpc:
            # test add_all call, note max samples of 1 with 1 link, should be quick
            # edit: quick = 22 minutes!
            ret = cluster_rpc.\
                    ccarsjobsposting_service.add_all(maximum_links=1)
            self.assertGreater(ret['nLinks'], 0, "RPC etl.vt.add_all did not write at least 1 link!")

            # test get_stats, should have stuff in job_postings
            ret = json.loads(cluster_rpc.ccarsjobsposting_service.get_stats())
            self.assertIsNotNone(ret, "RPC etl.vt.get_stats failed!")
            self.assertGreater(ret['count'], 0,\
                    "etl.vt.get_stats indicates that database has more than 0 postings!"\
                    "Need to start with fresh, wiped, database!")

    @classmethod
    def tearDownClass(cls):
        # it takes about 15 seconds for the containers to shut down
        assert cls.dockercompose.run(cmd='down', service=None, yml=None), "Was not able to run docker-compose down"
