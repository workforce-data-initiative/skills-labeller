""" Unit test for job posting preprocessor """
import unittest
from labeller import JobPostingPreprocessor


class TestJobProcessingPreprocessor(unittest.TestCase):
    """ Unit test for job preprocessor """

    def setUp(self):
        self.preprocessor = JobPostingPreprocessor()

    def test_preprocessor(self):
        text = "fox fox fox multi tool jumped over the fence and and"
        features = self.preprocessor.get_job_posting_features(text=text)
        self.assertTrue(len(features) > 0)
