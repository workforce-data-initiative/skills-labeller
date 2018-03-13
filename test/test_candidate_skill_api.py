""" Unit test for candidate skill api"""
import unittest
import requests
import json
import os
import subprocess
import time
import pymongo
from skills_utils.iteration import Batch
from etl.utils.mongo import MongoDatabase
try:
    from nameko.standalone.rpc import ClusterRpcProxy
except ImportError:
    raise ImportError("This unittest requires Nameko to be installed. You can install it with `pip install nameko`")

# Note: we should really make this part of a utils file in tests :-/
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

class TestCandidateSkillSelector(unittest.TestCase):
    """ Unit test for candidate skill api"""

    @classmethod
    def setUpClass(cls,
                   v3_api_filename="v3_ccars.json",
                   test_dir="test"):
        """
        Prepopulate job_postings in advance of this test, using
        stock test data from CCARS VT
        """
        cls.dockercompose = DockerCompose()
        assert cls.dockercompose.run(cmd='up', service='etl'), "Was not able to run docker-compose up"
        # this should more intelligent, like query service ips, return when a
        # 3 services are up and amqp is responding
        time.sleep(30)

        # Check that key services are up and running
        # should probably pull this name out of a config file as well .. :-/
        cls.rabbit_ip = cls.dockercompose.extract_service_ip('rabbit')
        assert len(cls.rabbit_ip.split('.')) == 4, "Rabbit MQ service ip is malformed/None!"
        #service_ip = cls.dockercompose.extract_service_ip('skill_candidates')
        #assert len(service_ip.split('.')) == 4, "Skill Candidates service ip is malformed!"

        # assumes the rabbit mq config hasn't changed, should be read in from a config file :-/
        cls.config = {
            'AMQP_URI': 'amqp://guest:guest@{service_ip}:5672'.format(service_ip=cls.rabbit_ip)
        }

        cls.batch_size = 100
        cls.mongo = MongoDatabase()
        cls.v3_api_filename = os.path.join(test_dir, v3_api_filename)

        with open(cls.v3_api_filename, 'r') as fp:
            for batch in Batch(fp, cls.batch_size):
                requests = []
                for job_json in batch:
                    parsed = json.loads(job_json)
                    parsed['_id'] = parsed['id']
                    requests.append(pymongo.UpdateOne(
                        {'_id': parsed['_id']},
                        {'$set': parsed},
                        upsert=True
                    ))
                resp = cls.mongo.db.job_postings.bulk_write(requests, ordered=False)
        count = cls.mongo.db.command({'collstats':'job_postings'})["count"]
        assert count > 0, "Did not prepopulate database with job_postings!"

    def test_generate_candidates(self):
        with ClusterRpcProxy(self.config) as cluster_rpc:
            cluster_rpc.skill_candidates.generate_candidates()

        count = self.mongo.db.command({'collstats':'candidate_skills'})["count"]
        self.assertGreater(count, 0, "Skill Candidates database has no candidates!")

    @classmethod
    def tearDownClass(cls):
        cls.mongo.db.job_postings.drop()
        cls.mongo.db.skill_candidates.drop()
