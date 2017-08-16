import wabbit_wappa # for Vowpal Wabbit via Python
import pymongo
import json

class OrderImportances(object):
    def __init__(self,
                 sample_size=None,
                 host=None,
                 database="skills_labeller",
                 collection="unlabeled_text",
                 port=27017):
        self.sample_size = sample_size
        self.host = host
        self.collection = collection

        if not self.sample_size:
            self.sample_size = -1 # indicates that we order the entire database

        if not host:
            self.host = 'localhost'

        self.client = pymongo.MongoClient(self.host,
                                          self.port,
                                          maxPoolSize=50)
        self.db = self.client[database]

    def get_job_postings(self, collection=None, sample_size=None):
        sample_size = sample_size
        collection=collection

        if not collection:
            collection = self.collection

        if not sample_size:
            sample_size = self.sample_size

        if -1 == sample_size:
            sample_size = self.db[collection].count()
