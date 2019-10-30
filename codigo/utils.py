import glob
import os
import sys
import time

import pandas as pd
import simplejson as json
from pymongo import MongoClient


def today():
    return '' + time.strftime('%Y%m%d')


def hour():
    return '' + time.strftime('%H%M%S')


def parse_tweet(j):
    try:
        tt = {'geo': j['geo'], 'entities': j['entities'], 'tweet': j['text'], 'screenName': j['user']['screen_name']}
        return json.dumps(tt)
    except KeyError:
        print("key error" + sys.exc_info()[1] + today().strftime('%Y-%m-%d %H:%M:%S'))
        return json.dumps(j)


def get_latest_output():
    cwd = os.getcwd()

    all_files = glob.glob(cwd + "/Output*.csv")

    return all_files[-1]


def combine_csv(all_files):
    # Idea to combine csv files
    combined_csv = pd.concat([pd.read_csv(f) for f in all_files])
    combined_csv.to_csv("combined_csv.csv", index=False, encoding='utf-8-sig')


def extract_hash_tags(s):
    res = set(part[1:] for part in s.split() if part.startswith('#'))
    if res:
        return res
    else:
        return res


def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)

    return conn[db]


def read_mongo(db, collection, query_condition={}, query_fields={}, host='localhost', port=27017, username=None,
               password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    supress = 1
    if no_id:
        suppress = 0

    query_fields["_id"] = suppress

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query_condition, query_fields)

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    return df


if __name__ == '__main__':
    df = read_mongo('dbTweets', 'tweets_chile', query_fields={"text": 1})
