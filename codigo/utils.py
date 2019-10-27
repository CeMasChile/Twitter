import glob
import sys
import os
import time

import simplejson as json
import pandas as pd

import re


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
    return set(part[1:] for part in s.split() if part.startswith('#'))


if __name__ == '__main__':
    print(extract_hash_tags('"I love #stackoverflow because #people are very #helpful!"'))
