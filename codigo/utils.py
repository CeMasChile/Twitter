import datetime
import glob
import os
import sys
import time
from datetime import datetime

import pandas as pd
import json
from bson.json_util import dumps
from pymongo import MongoClient


def today():
    return '' + time.strftime('%Y%m%d')


def hour():
    return '' + time.strftime('%H%M%S')


def parse_tweet(j):
    """
    Parses a dictionary created from a tweepy Status object
    into a JSON formatted string.
    :param j: dict
    """

    # Retrieve full text in case it is truncated
    if "retweeted_status" in j.keys():
        try:
            text = j["retweeted_status"]["extended_tweet"]["full_text"]
        except KeyError:
            text = j["retweeted_status"]["text"]
    else:
        try:
            text = j["extended_tweet"]["full_text"]
        except KeyError:
            text =  j["text"]

    # Create custom json with only the useful info.
    try:
        tt = {'dateTweet': j['created_at'],
              'tweet': text,
              'screenName': j['user']['screen_name'],
              'name': j['user']['name'],
              'user_url': j['user']['url'],
              'description': j['user']['description'],
              'location': j['user']['location'],
              'verified': j['user']['verified'],
              'geoEnabled': j['user']['geo_enabled'],
              'hash_tags': j['hash_tags']
              }
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
               password=None, no_id=True, num_limit=None, json_only=False):
    """ Read from Mongo and Store into DataFrame or return JSON """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    suppress = 1
    if no_id:
        suppress = 0

    # query_fields["_id"] = suppress

    # Make a query to the specific DB and Collection
    if(num_limit is None):
        cursor = db[collection].find(query_condition, query_fields)
    else:
        cursor = db[collection].find(query_condition, query_fields).sort('_id',-1).limit(num_limit)

    # JSON return
    if json_only:
        return dumps(cursor)

    # Expand the cursor and construct the DataFrame
    return pd.DataFrame(list(cursor))


def json_pandas(json_string):
    return pd.read_json(json_string)


if __name__ == '__main__':
    df = read_mongo('dbTweets', 'tweets_chile', query_fields={"text": 1, "user": 1})
    print(df)
