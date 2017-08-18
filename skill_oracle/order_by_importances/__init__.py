import wabbit_wappa # for Vowpal Wabbit via Python
from random import random
import itertools
import pymongo
import json

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

    def get_all_importances(self, vw=None):
        """
        Get importances from Vowpal Wabbit/ML System
        """
        for batch in self.get_all_job_postings(yield_n_postings=3):
            importances = []
            for posting in batch:
                # would use vw object to get prediction, extract importance value
                # importances = vw.send(... examples ...)
                importances.append(random())
                yield zip(batch, importances)

    def set_random_importances(self):
        """
        Set random importances in data store; used for simple testing
        """
        for ret in self.get_all_importances():
            batch, importances = next(ret)
            # todo: upsert many

    def sample_job_postings(self, collection_name=None, sample_size=None, yield_n_postings=10):
        """
        WIP
        """
        ret = []
        sample_size = sample_size
        collection_name=collection_name

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
        collection_name=collection_name

        if not collection_name:
            collection_name = self.collection_name

        for count, doc in enumerate(self.db[collection_name].find()):
            if 0 == count % yield_n_postings:
                yield ret
                ret = []

            ret.append(doc)

        yield ret # at end of docs
