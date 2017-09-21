import wabbit_wappa  # for Vowpal Wabbit via Python
from random import random
import itertools
import pymongo
import json
import ipdb
try:
    from labeller import MongoDatabase
except:
    from ..db.mongo import MongoDatabase


class OrderImportances(object):
    """
    WIP not done yet
    """

    def __init__(self,
                 sample_size=None,
                 host=None,
                 database="skills_labeller",
                 collection_name="unlabeled_text",
                 port=27017):

        self.sample_size = sample_size
        self.host = host
        self.collection_name = collection_name
        self.port = port

        if not host:
            self.host = 'localhost'

        self.client = pymongo.MongoClient(self.host,
                                          self.port,
                                          maxPoolSize=50)
        self.db = self.client[database]
        self.collection = self.db[self.collection_name]

    def get_all_vw_importances(self, collection_name=None, vw=None):
        """
        Get importances from Vowpal Wabbit/ML System

        Think about efficient batching (I know you can send multiple examples
        within one send call)

        WIP, not implemented beyond what's needed for unittests yet
        """
        collection_name = collection_name
        if not collection_name:
            collection_name = self.collection_name

        # note: yield n should be a parameter, class defined
        for postings in self.get_all_job_postings(collection_name=collection_name, yield_n_postings=3):
            # Strawperson implementation
            yield [{'job_posting': posting, 'vw_importance': random()} for posting in postings]

    def set_vw_importances(self, collection_name=None):
        """
        Apply VW to collection, update importances in collection
        """
        collection_name = collection_name
        if not collection_name:
            collection_name = self.collection_name

        for items in self.get_all_vw_importances(collection_name=collection_name):
            requests = [pymongo.UpdateOne({'_id': item['job_posting']['_id']},
                                          {"$set": {'importance': item['vw_importance']}})
                        for item in items]

            result = self.db[collection_name].bulk_write(
                requests, ordered=False)
            assert result.modified_count == len(
                requests), "Was not able to bulk write each request"

    def sample_job_postings(self, collection_name=None, sample_size=None, yield_n_postings=10):
        """
        WIP
        """
        ret = []
        sample_size = sample_size
        collection_name = collection_name

        if not collection_name:
            collection_name = self.collection_name

        if not sample_size:
            sample_size = self.sample_size

        if -1 == sample_size:
            sample_size = self.db[collection_name].count()
        pass

    def get_all_job_postings(self, collection_name=None, yield_n_postings=10):
        """
        """

        ret = []
        collection_name = collection_name

        if not collection_name:
            collection_name = self.collection_name

        doc = None
        for count, doc in enumerate(self.db[collection_name].find(), 1):
            ret.append(doc)
            if 0 == count % yield_n_postings:
                yield ret
                ret = []

        if [] != ret:  # return any left over postings modulo n_postings
            ret.append(doc)
            yield ret  # at end of docs

if __name__ == "__main__":
    import time
    while True:
        time.sleep(1)
        print("\n\t stub loop for sampling from database")
