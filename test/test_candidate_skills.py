""" Unit test for candidate skill selector"""
from etl.utils.mongo import MongoDatabase
from etl.vt import CCARSJobsPostings
from etl.vt import SkillCandidates
import os
import json
import shutil
import unittest
from unittest.mock import patch

class InstantiateDatabase(object):
    """
    Class for instatiating the database so that
    candidate skills may be extracted from it, is quite
    duplicative of the test_etl.py but kept seperate for
    independence purposes.
    """
    def __init__(self,
                 num_test_items=3,
                 test_dir="test",
                 v3_api_filename="v3_ccars.json"):
        self.ccars = CCARSJobsPostings()
        self.v3_api_filename = os.path.join(test_dir, v3_api_filename)
        self.num_test_items = num_test_items
        self.v3_dst_file_path = None

        self.patcher = patch('etl.vt.CCARSJobsPostings.write_url', spec=True)
        self.mock_write_url = self.patcher.start()
        self.mock_write_url.side_effect = self.copy_v3_test_file

        self.ccars.add_all()

    def __del__(self):
        self.undo_mock_write_url()
        self.patcher.stop()

    def copy_v3_test_file(self, link, file_path):
        """
        Simulates the result of successfully downloading V3
        CCARS Job posting data and writing it to disk
        """
        link = self.v3_api_filename
        shutil.copyfile(link, file_path)
        self.v3_dst_file_path = file_path # for removal

    def undo_mock_write_url(self):
        """
        Undos the side_effect of mock_write_url
        """
        self.ccars._drop_db()
        if os.path.isfile(self.v3_dst_file_path):
            os.remove(self.v3_dst_file_path)

class TestCandidateSkills(unittest.TestCase):
    """ Unit test for ETL class"""
    @classmethod
    def setUpClass(cls):
        cls.db = InstantiateDatabase()

    @classmethod
    def tearDownClass(cls):
        cls.db.__del__() # todo: does not seem to clear db?

    def test_candidates_init(self):
        candidates = SkillCandidates()
        assert isinstance(candidates.preprocessor, list),\
                "Preprocessor label is not of type list ({})".format(type(candidates.preprocessor))

    def test_candidates_generate(self):
        candidates = SkillCandidates()
        candidates.generate_candidates()

        db = MongoDatabase()
        ret = db.sample_candidate(size=1)
        assert len(ret[0]) >= 4, "Expected at least 4 fields in sample! ({})".format(len(ret[0]))
        assert len(ret) == 1, "Expected one sample! ({})".format(len(ret))
