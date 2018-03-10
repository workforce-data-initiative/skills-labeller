""" Unit test for candidate skill selector"""
from etl.vt import CCARSJobsPostings
import os
import json
import shutil
import unittest
from unittest.mock import patch

class TestETL(unittest.TestCase):
    """ Unit test for ETL class"""
    def setUp(self,
              test_dir="test",
              v3_api_filename="v3_ccars.json",
              num_test_items=3):
        #self.mock_write_url = patch('etl.vt.CCARSJobsPostings.write_url').start()

        self.ccars = CCARSJobsPostings()
        self.v3_api_filename = os.path.join(test_dir, v3_api_filename)
        self.num_test_items = num_test_items
        self.v3_dst_file_path = None

    def tearDown(self):
        pass

    def copy_v3_test_file(self, link=None, full_path=None):
        """
        Simulates the result of successfully downloading V3
        CCARS Job posting data and writing it to disk
        """
        link = self.v3_api_filename
        shutil.copyfile(link, full_path)
        self.v3_dst_file_path = full_path

    def undo_mock_write_url(self):
        """
        Undos the side_effect of mock_write_url
        """
        self.ccars._drop_db()

        if os.path.isfile(self.v3_dst_file_path):
            os.remove(self.v3_dst_file_path)

    def test_db_connectivity(self):
        return self.ccars.check_mongo()

    def test_load_all_V3_API(self):
        with patch('etl.vt.CCARSJobsPostings.write_url') as mock_write_url:
            mock_write_url.side_effect = self.copy_v3_test_file

            all_stats = self.ccars.add_all() # indirectly calls our mocked write_url
            assert 1 == all_stats['nLinks'], 'Expected number of test downloads did not occur!'

        # Undo any and all side effects
        self.undo_mock_write_url()

    def test_get_stats(self):
        with patch('etl.vt.CCARSJobsPostings.write_url') as mock_write_url:
            mock_write_url.side_effect = self.copy_v3_test_file

            all_stats = self.ccars.add_all() # indirectly calls our mocked write_url
            stats = json.loads(self.ccars.get_stats())
            assert self.num_test_items == stats['count'],\
                "Expected number of items not in databse, found {}".format(stats['count'])
            assert 0 == stats['number_sampled'] == stats['number_not_sampled'],\
                "Found non-zero number of sampled, not sampled items! Expected none."

        # Undo any and all side effects
        self.undo_mock_write_url()
