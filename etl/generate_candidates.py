from utils.mongo import MongoDatabase
import json
import logging
import urllib.request
import urllib.parse
import re

PREPROCESSOR_URL = 'http://localhost:3000/'

def generate_candidates(preprocessor='default', key='jobDescription', db_class=MongoDatabase):
    db = db_class()
    for job_posting, job_posting_id in db.get_job_postings_and_ids():
        job_posting_text = job_posting[key]
        data = urllib.parse.urlencode(dict(
            job_posting=job_posting_text,
            n_keyterms=0.05
        ))
        req = urllib.request.Request(PREPROCESSOR_URL + '?' + data)
        resp = urllib.request.urlopen(req)
        respText = resp.read().decode('utf-8')
        respJson = json.loads(respText)
        for preprocessor, candidate_matches in respJson['preprocesser']['potential_skills'].items():
            logging.info(candidate_matches)
            for candidate_match in candidate_matches:
                logging.info(
                    'Match: %s, context: %s',
                    candidate_match['token_phrase'],
                    job_posting_text[candidate_match['context_span'][0]:candidate_match['context_span'][1]]
                )
                db.insert_candidate_skill(
                    job_posting_id=job_posting_id,
                    token_span=candidate_match['token_span'],
                    context_span=candidate_match['context_span'],
                    key=key,
                    expected_label=1,
                    preprocessor_id=preprocessor
                )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_candidates()
