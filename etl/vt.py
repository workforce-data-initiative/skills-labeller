""" A simple Extract, Transfer, Load utility. """
import os
import logging
import re
import json
import urllib.request
import urllib.parse
from collections import Counter
import pymongo
from nameko.rpc import rpc
from etl.utils.mongo import MongoDatabase
from skills_utils.iteration import Batch
from etl.preprocessor import SingleRankWithContext

VT_DATASET_LINK_REGEX = "<a\s+href=\"(\S+).json\""
VT_ROOT_URL = "http://opendata.cs.vt.edu"
VT_DATA_URL = VT_ROOT_URL + "/dataset/openjobs-jobpostings"
VT_DATASETS = '/skills-labeller/resources'

TOTAL_SAMPLES = 1000
BATCH_SIZE = 100

class CCARSJobsPostings(object):
    """
    An class providing access to CCARS' Open Data Open Jobs dataset (CCARS)
    (see: https://opendata-cs-vt.github.io/ccars-jobpostings/)
    as well as methods for getting more CCARS data.

    note: this class might be moved, dramatically changed or even replaced with
    a call out to a publically availabel WDI database, since job data etl
    is addressed by several other WDI projects. This class partially included
    as more of a proof concept for alpha version work and label generation.
    """
    name = "ccarsjobsposting_service"
    #dispatcher_rpc = RpcProxy("dispatcher") # note: use fast RPC service

    def __init__(self,
                 vt_root_url=VT_ROOT_URL,
                 vt_data_url=VT_DATA_URL,
                 vt_datasets=VT_DATASETS,
                 vt_dataset_link_regex=VT_DATASET_LINK_REGEX,
                 default_total_samples=TOTAL_SAMPLES,
                 default_batch_size=BATCH_SIZE):
        self.mongo = MongoDatabase()
        self.total_samples = default_total_samples
        self.batch_size = default_batch_size

        self.vt_datasets = vt_datasets
        self.vt_root_url = vt_root_url
        self.vt_data_url = vt_data_url
        self.vt_datasets_link_regex = vt_dataset_link_regex

    @rpc
    def check_mongo(self):
        ret = False
        if self.mongo.db:
            ret = True
        return ret

    def _drop_db(self):
        self.mongo.db.job_postings.drop()

    @rpc
    def get_stats(self):
        ret = {}
        count = self.mongo.db.command({'collstats':'job_postings'})["count"]
        number_sampled = self.mongo.db.job_postings.count(\
                {"sampled": {"$exists":"true"}})
        number_not_sampled = self.mongo.db.job_postings.count(\
                {"sampled": {"$exists":"false"}})
        ret['count'] = count
        ret['number_sampled'] = number_sampled
        ret['number_not_sampled'] = number_not_sampled

        return json.dumps(ret)

    def write_url(self, link=None, full_path=None):
        urllib.request.urlretrieve(link, full_path)

    @rpc
    def add_all(self, maximum_links=None, total_samples=None):
        """ Load all the Virginia Tech job listings.
            Note: this is very slow, needs some profling and
            inspection. Alternatively, a different database might
            be used instead, although I think mongo can be made
            fast enough
        """
        mongo = self.mongo

        if not total_samples:
            total_samples = self.total_samples

        req = urllib.request.Request(self.vt_data_url)
        resp = urllib.request.urlopen(req)
        respData = resp.read()
        links = re.findall(self.vt_datasets_link_regex, str(respData))
        logging.info('Read links on VT page, found %s', len(links))

        for link_count, link in enumerate(links[0:1], start=1):
            if maximum_links:
                if link_count > maximum_links:
                    break

            logging.info('On link #: %s',link_count)

            link += '.json'
            logging.info('Downloading dataset %s', link)
            leaf_filename = link.split('/')[-1]
            full_filename = os.path.join(self.vt_datasets, leaf_filename)
            all_stats = Counter()

            if not os.path.exists(full_filename):
                self.write_url(link=link, full_path=full_filename)
                print('Processing dataset {0}'.format(leaf_filename))

                dataset_stats = Counter()
                with open(full_filename, 'r') as fp:
                    total_seen = 0
                    for batch in Batch(fp, self.batch_size):
                        total_seen += self.batch_size
                        if total_seen > total_samples:
                            break
                        logging.info('Processing batch')
                        requests = []
                        for job_json in batch:
                            parsed = json.loads(job_json)
                            parsed['_id'] = parsed['id']
                            requests.append(pymongo.UpdateOne(
                                {'_id': parsed['_id']},
                                {'$set': parsed},
                                upsert=True
                            ))
                        logging.info('Created batch')
                        # is there a way to tell mongo to pull .json from a url intead of having to pull them and push
                        # again?
                        result = mongo.db.job_postings.bulk_write(requests, ordered=False)
                        for key in ['nInserted', 'nMatched', 'nModified', 'nRemoved', 'nUpserted']:
                            dataset_stats[key] += result.bulk_api_result[key]
                        logging.info('Successfully wrote batch. total seen: %s details: %s', total_seen, result.bulk_api_result)

                    logging.info('Successfully wrote dataset. details: %s', dataset_stats)
                    for key in ['nInserted', 'nMatched', 'nModified', 'nRemoved', 'nUpserted']:
                        all_stats[key] += dataset_stats[key]

                    all_stats['nLinks'] = link_count

            logging.info('Successfully wrote all datasets. details: %s', all_stats)

            return all_stats

class SkillCandidates(object):
    name = "skill_candidates"
    #ccarsjobsposting_rpc = RpcProxy("ccarsjobsposting_service") # note: use fast RPC service
    #dispatcher_rpc = RpcProxy("dispatcher") # note: use fast RPC service

    def __init__(self, preprocessor=['default'], n_keyterms=0.05):
        self.preprocessor = preprocessor
        self.preprocessors = {}

        for label in preprocessor:
            if label == 'default':
                self.preprocessors[label] = SingleRankWithContext(n_keyterms=n_keyterms)

    @rpc
    def generate_candidates(self,
                            key='jobDescription',
                            db_class=MongoDatabase):
        db = db_class()
        for job_posting, job_posting_id in db.get_job_postings_and_ids():
            job_posting_text = job_posting[key]
            for label in self.preprocessors.keys():
                candidates = self.preprocessors[label].\
                        get_job_posting_keyterms(text=job_posting_text)

                for candidate in candidates:
                    logging.info(candidate)
                    logging.info(
                        'Match: %s, context: %s',
                        candidate['token_phrase'],
                        job_posting_text[candidate['context_span'][0]:candidate['context_span'][1]]
                    )
                    db.insert_candidate_skill(
                        job_posting_id=job_posting_id,
                        token_span=candidate['token_span'],
                        context_span=candidate['context_span'],
                        key=key,
                        expected_label=1,
                        preprocessor_id=label
                    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #load_all_vt_datasets()
