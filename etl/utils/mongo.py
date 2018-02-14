""" A MongoDB ORM wrapper. """
import os
import pymongo
import random
import logging


class MongoDatabase(object):
    """ MongoDB ORM. """

    # __slots__ = ['MONGO_HOST', 'MONGO_PORT', 'MONGO_DATABASE',
    #              'MONGO_USERNAME', 'MONGO_PASSWORD' 'client', 'db']

    def __init__(self):
        self.MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
        self.MONGO_PORT = os.getenv('MONGO_PORT', 27017)
        self.MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'skills-labeller')
        self.MONGO_USERNAME = os.getenv('MONGO_USERNAME', None)
        self.MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', None)
        self.candidates = "candidate_skills"

        if not self.MONGO_USERNAME or not self.MONGO_PASSWORD:
            self.client = pymongo.MongoClient(
                self.MONGO_HOST, int(self.MONGO_PORT))
        else:
            connection = "mongodb://{0}:{1}@{2}:{3}/{4}".format(
                self.MONGO_USERNAME, self.MONGO_PASSWORD,
                self.MONGO_HOST, self.MONGO_PORT, self.MONGO_DATABASE)
            self.client = pymongo.MongoClient(connection)
        self.db = self.client[self.MONGO_DATABASE]

    def create_job_posting(self, posting):
        """ Creates a new job posting entry.

        Parameters
        ----------
        posting: dict
            A dictionary containing the job posting to add.

        Returns
        -------
        result: str
            MongoDB object ID if the object was successfully added or None if
            not created.

        """
        try:
            result = self.db.job_postings.insert_one(posting).inserted_id
            logging.info('Successfully created job posting with object id %s', result)
        except Exception as e:
            result = None
            logging.warning('Job posting creation for input %s unsuccessful! Reason: %s', posting, e)
        return result

    def get_random_posting(self):
        """ Retrieve a random job posting from the collection.

        Returns
        -------
        posting: dict
            A random job posting.

        """

        count = self.db.job_postings.count()
        logging.info('Selecting random job posting from %s total', count)
        index = random.randrange(1, count - 1)
        sample = self.db.job_postings.find().limit(-1).skip(index).next()
        sample['_id'] = str(sample['_id'])
        logging.info('Returning random job posting with id %s', sample['_id'])
        return sample

    def get_job_postings_and_ids(self):
        postings = []
        for posting in self.db.job_postings.find().limit(1):
            postings.append((posting, posting['_id']))
        return postings

    def insert_candidate_skill(self, job_posting_id, token_span, context_span, key, expected_label, preprocessor_id):
        insert_object = {
            'job_posting_id': job_posting_id,
            'token_span': token_span,
            'context_span': context_span,
            'key': key,
            'expected_label': expected_label,
            'preprocessor_id': preprocessor_id,
            'labelling_events': [],
        }
        self.db.candidate_skills.insert_one(insert_object)

    def sample_candidate(self, sampled=None, size=1):
        ret = []
        query_sampled = sampled
        query_filter = [{'$match':{'sampled':{'$exists':query_sampled}}}]
        query_filter.append({'$sample': {'size':size}})

        response = self.db[self.candidates].aggregate(query_filter)
        #result = [r for r in response][0]
        for result in response:
            job_posting = self.db.job_postings.find_one({'_id': result['job_posting_id']})
            key = result['key']
            key_text = job_posting[key]
            sample = {
                'context': key_text[result['context_span'][0]:result['context_span'][1]],
                'token': key_text[result['token_span'][0]:result['token_span'][1]],
                'expected_label': result['expected_label'],
                'preprocessor_id': result['preprocessor_id']
            }
            ret.append(sample)

            # label sample as having been sampled, might be better as a bulk update?
            self.db.candidate_skills.update({'_id':result["_id"]}, {"$set": {"sampled":True}})

        return ret
