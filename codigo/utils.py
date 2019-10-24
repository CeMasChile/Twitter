import sys
from datetime import date

import simplejson as json


def today():
    return " " + date.today().strftime('%Y-%m-%d %H:%M:%S')


def parse_tweet(j):
    try:
        tt = {'geo': j['geo'], 'entities': j['entities'], 'tweet': j['text'], 'screenName': j['user']['screen_name']}
        return json.dumps(tt)
    except KeyError:
        print("key error" + sys.exc_info()[1] + today().strftime('%Y-%m-%d %H:%M:%S'))
        return json.dumps(j)
