""" A simple Extract, Transfer, Load utility. """

import os
import sys
import re
import json
import urllib.request
import urllib.parse
import contextlib
from collections import OrderedDict
from labeller import MongoDatabase

VT_DATASET_LINK_REGEX = "<a\s+\S+\s+href=\"(\S+)\""
VT_DATASET_REGEX = "<a\s+href=\"(\S+)\""
VT_ROOT_URL = "http://opendata.cs.vt.edu"
VT_DATA_URL = VT_ROOT_URL + "/dataset/openjobs-jobpostings"
VT_DATASETS = './resources'


def load_all_vt_datasets():
    """ Load all the Virginia Tech job listings. """
    db = MongoDatabase()

    if os.path.exists(VT_DATASETS) and os.path.isdir(VT_DATASETS):
        datasets = os.listdir(VT_DATASETS)
        for dataset in datasets:
            if dataset.endswith('.json'):
                print('Processing dataset {0}'.format(dataset))
                dataset_path = os.path.join(VT_DATASETS, dataset)
                with open(dataset_path, 'r') as fp:
                    job_postings = fp.readlines()

                for job_posting in job_postings:
                    job_posting_dict = json.loads(job_posting)

                    # create the derived job posting entry.
                    job_posting_entry = OrderedDict()
                    db.create_job_posting(job_posting_dict)


if __name__ == '__main__':
    load_all_vt_datasets()
