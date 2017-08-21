""" A MongoDB ORM wrapper. """

import os
import sys
import pymongo
import random
import json
import logging
import urllib.request
import urllib.parse
import contextlib
from bson.objectid import ObjectId


class MongoDatabase(object):
    """ MongoDB ORM. """

    __slots__ = ['MONGO_HOST', 'MONGO_PORT', 'MONGO_DATABASE', 'client', 'db']

    def __init__(self):
        self.MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
        self.MONGO_PORT = os.getenv('MONGO_PORT', 27017)
        self.MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'skills-labeller')
        self.client = pymongo.MongoClient(self.MONGO_HOST, self.MONGO_PORT)
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
        except:
            result = None
        return result

    def get_random_posting(self):
        """ Retrieve a random job posting from the collection.

        Returns
        -------
        posting: dict
            A random job posting.

        """

        count = self.db.job_postings.count()
        index = random.randrange(1, count-1)
        sample = self.db.job_postings.find().limit(-1).skip(index).next()
        sample['_id'] = str(sample['_id'])
        return sample
