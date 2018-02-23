""" Unit test for job posting preprocessor """
from etl.preprocessor import SingleRankWithContext
import unittest

class TestJobProcessingPreprocessor(unittest.TestCase):
    """ Unit test for job preprocessor """

    def setUp(self):
        self.preprocessor = SingleRankWithContext()

    def test_default_singlerank_preprocessor(self):
        text = """Job is located in Jacksonville, FL. Adjunct Instructor - Cosmetology Under general supervision, plans and implements curriculum and educational programs for students within the program. Communicates class content to students so that learning occurs, skills are developed, and students are motivated to learn and achieve their educational objectives."""
        n_keyterms = 0.05

        potential = self.preprocessor.get_job_posting_keyterms(text=text, n_keyterms=n_keyterms)
        self.assertEqual(
            sorted(list(set(row['token_phrase'] for row in potential))),
            ['educational', 'educational programs', 'students']
        )
        for row in potential:
            # make sure all rows have the right keys
            self.assertIn('token_span', row)
            self.assertIn('token_phrase', row)
            self.assertIn('context_span', row)

            # ensure that *all* returned spans match the phrase
            # in other words, that nothing gets mangled by
            # preprocessing/lemmatization
            self.assertEqual(
                text[row['token_span'][0]:row['token_span'][1]],
                row['token_phrase']
            )

        # assert a little bit about the context of one of them
        # with fixed input we should be able to assert some specifics
        # about the output without worrying about the variability
        first_expected = {
            'token_phrase': "educational programs",
            'token_span': (132, 152),
            'context_span': (82, 202)
        }
        self.assertEqual(potential[0], first_expected)
