import logging
import sys
import time
from datetime import date

import simplejson as json
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import config
from main import get_keywords

def today():
    return " " + date.today().strftime('%Y-%m-%d %H:%M:%S')


def parse_tweet(j):
    try:
        tt = {}
        tt['geo'] = j['geo']
        tt['entities'] = j['entities']
        tt['tweet'] = j['text']
        tt['screenName'] = j['user']['screen_name']
        return json.dumps(tt)
    except KeyError:
        print("key error" + sys.exc_info()[1] + today().strftime('%Y-%m-%d %H:%M:%S'))
        return json.dumps(j)


class StreamListener(StreamListener):

    def on_status(self, status):
        print(status.author.screen_name, status.created_at, status.text)
        # Writing status data
        # with open('OutputStreaming.txt', 'a') as f:
        #    writer = csv.writer(f)
        #    writer.writerow([status.author.screen_name, status.created_at, status.text])

    def on_limit(self, status):
        print("Rate Limit Exceeded, Sleep for 15 Mins")
        time.sleep(15 * 60)
        return True

    def on_error(self, status_code):
        print('Encountered error with status code:', status_code)
        return True  # Don't kill the stream

    def on_timeout(self):
        print('Timeout...')
        return True  # Don't kill the stream

    def on_data(self, data):
        json_data = json.loads(data)
        print(json_data)
        if data[0].isdigit():
            pass
        elif json_data['geo'] is not None:
            tt = parse_tweet(json_data)
            print(json_data)


def read_tweets(region, track):
    # AUTH #
    auth = OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    l = StreamListener()

    streamer = Stream(auth=auth, listener=l, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    print("tracking languages {0} location {1} track {2}".format('es', region, track))

    streamer.filter(locations=region, languages='es', track=track)


def main():
    # Parametros de busqueda #
    search_words = get_keywords()

    # Get Tweets #
    read_tweets(config.region, search_words)


if __name__ == "__main__":
    main()
