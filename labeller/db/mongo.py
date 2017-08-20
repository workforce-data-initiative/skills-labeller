""" A MongoDB ORM wrapper. """

import os
import sys


class MongoDatabase(object):
    """ MongoDB ORM. """

    __slots__ = ['MONGO_HOST', 'MONGO_PORT']

    def __init__(self):
        self.MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
        self.MONGO_PORT = os.getenv('MONGO_PORT', 27017)
        self.MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'skills_labeller')
