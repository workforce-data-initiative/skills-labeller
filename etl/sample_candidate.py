from utils.mongo import MongoDatabase
import json
import logging
import urllib.request
import urllib.parse
import re

PREPROCESSOR_URL = 'http://localhost:3000/'


def sample_candidate():
    db = MongoDatabase().db
    result = [r for r in db.candidate_skills.aggregate([{'$sample': {'size': 1}}])][0]
    logging.info(result)
    job_posting = db.job_postings.find_one({'_id': result['job_posting_uuid']})
    key_text = job_posting['insertOne']['document'][result['key']]
    logging.info(key_text[result['token_span'][0]:result['token_span'][1]])
    logging.info(key_text[result['context_span'][0]:result['context_span'][1]])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sample_candidate()
