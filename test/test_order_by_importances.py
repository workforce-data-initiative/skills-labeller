""" Unit test for job posting preprocessor """
import unittest
import pymongo
import json
from itertools import chain
from random import random  # should we consider using a real random generator?
import ipdb
from labeller import OrderImportances


class TestOrderImportance(unittest.TestCase):
    """ Unit test for job preprocessor """

    def setUp(self,
              host=None,
              database="skills_labeller",
              collection_name="test_unlabeled_text",
              port=27017):

        example_job_posting_text = "Inevitably, then, corporations do not restrict themselves merely to the arena of economics. Rather, as John Dewey observed, 'politics is the shadow cast on society by big business'. Over decades, corporations have worked together to ensure that the choices offered by 'representative democracy' all represent their greed for maximised profits. This is a sensitive task. We do not live in a totalitarian society - the public potentially has enormous power to interfere. The goal, then, is to persuade the public that corporate-sponsored political choice is meaningful, that it makes a difference. The task of politicians at all points of the supposed 'spectrum' is to appear passionately principled while participating in what is essentially a charade."
        self.host = host
        self.collection_name = collection_name
        self.port = port

        if not host:
            self.host = 'localhost'

        if not collection_name:
            self.collection_name = 'test_unlabeled_text'

        # Assumes mongod running on host, port
        self.client = pymongo.MongoClient(self.host,
                                          self.port,
                                          maxPoolSize=50)
        self.db = self.client[database]
        self.collection = self.db[self.collection_name]
        # ... populate test collection with some content
        self.collection.remove()
        # should random seed be set?
        self.collection.insert_many([{'Example Job Posting': example_job_posting_text,
                                      'importance': random()}
                                     for i in range(10)])
        assert self.db[self.collection_name].count() == 10

        self.orderimportances = OrderImportances(
            collection_name=collection_name)

    def tearDown(self):
        self.collection.remove()  # note: deprecated

    def test_orderimportances(self):
        """
        Probablistically test that orderimportances works by setting to random values under set_vw_importances
        """
        # get docs as a flattened array for easier iteration over them
        old_docs = [item for sublist in
                    self.orderimportances.get_all_job_postings(collection_name=self.collection_name) for item in sublist]
        self.orderimportances.set_vw_importances(
            collection_name=self.collection_name)  # side effect on data store
        new_docs = [item for sublist in
                    self.orderimportances.get_all_job_postings(collection_name=self.collection_name) for item in sublist]

        ret = True
        for doc in old_docs:
            for new_doc in new_docs:
                new_id, new_importance = new_doc['_id'], new_doc['importance']
                old_id, old_importance = doc['_id'], doc['importance']
                if new_id == old_id:
                    if new_importance == old_importance:
                        ret = False  # very unlikely to have same value
                        break  # nice save for a O(n^2) run time ;)

        assert ret, "At least one importance value was not modified by set_random_importances()"
