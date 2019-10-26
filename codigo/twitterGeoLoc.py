import csv
import sys
import time
from datetime import timedelta
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import config
from main import get_keywords


class StreamListener(StreamListener):

    # Define a function that is initialized when the miner is called
    def __init__(self, api=None):
        # That sets the api
        self.api = api

        # Create a file with 'data_' and the current time
        self.filename = 'OutputStreaming' + '_' + time.strftime('%Y%m%d-%H%M%S') + '.csv'

        # Create a new file with that filename
        csvFile = open(self.filename, 'w')

        # Create a csv writer
        csvWriter = csv.writer(csvFile)

        # Write a single row with the headers of the columns
        csvWriter.writerow(['text',
                            'created_at',
                            'geo',
                            'lang',
                            'place',
                            'user.favourites_count',
                            'user.statuses_count',
                            'user.description',
                            'user.location',
                            'user.id',
                            'user.created_at',
                            'user.verified',
                            'user.url',
                            'user.listed_count',
                            'user.friends_count',
                            'user.name',
                            'user.screen_name',
                            'user.geo_enabled',
                            'id',
                            'favorite_count',
                            'retweeted',
                            'source',
                            'favorited',
                            'retweet_count'])

    def on_status(self, status):
        """
        Receives tweets that check the filters of the Stream.
        Prints them on screen.
        Writes them on .txt file.
        """
        # Open the csv file created previously
        csvFile = open(self.filename, 'a')

        # Create a csv writer
        csvWriter = csv.writer(csvFile)

        # Try to
        try:
            # On screen tweets #
            print(status.author.screen_name, status.created_at, status.text)

            # Write the tweet's information to the csv file
            csvWriter.writerow([status.text,
                                status.created_at-timedelta(hours=-3),
                                status.geo,
                                status.lang,
                                status.place,
                                status.user.favourites_count,
                                status.user.statuses_count,
                                status.user.description,
                                status.user.location,
                                status.user.id,
                                status.user.created_at,
                                status.user.verified,
                                status.user.url,
                                status.user.listed_count,
                                status.user.friends_count,
                                status.user.name,
                                status.user.screen_name,
                                status.user.geo_enabled,
                                status.id,
                                status.favorite_count,
                                status.retweeted,
                                status.source,
                                status.favorited,
                                status.retweet_count])

        # If some error occurs
        except Exception as e:
            # Print the error
            print(e)
            # and continue
            pass

        # Close the csv file
        csvFile.close()

        # Return nothing
        return



    def on_error(self, status_code):
        # Print the error code
        print('Encountered error with status code:', status_code)

        # If the error code is 401, which is the error for bad credentials
        if status_code == 401:
            # End the stream
            return False

        return True  # Don't kill the stream

    def on_timeout(self):
        # Print timeout message
        print(sys.stderr, 'Timeout...')

        # Wait 10 seconds
        time.sleep(10)

        return True  # Don't kill the stream

    '''
    # NOT WORKING YET#
    def on_data(self, data):
        json_data = json.loads(data)
        print(json_data)
        if data[0].isdigit():
            pass
        try:
            if json_data['geo'] is not None:
                tt = parse_tweet(json_data)
                print(tt)
        except Exception:
            print("error in geo")
    '''


def read_tweets(region, track):
    # AUTH #
    auth = OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    # API #
    l = StreamListener()

    # OUTPUT #
    filename = 'OutputStreaming'

    # INIT STREAM #
    streamer = Stream(auth=auth, listener=l)#, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    print("Tweets idioma: {0}, location: {1},  search_words: {2}, output: {3}".format('es', region, track, filename))
    print("")

    # FILTERS #
    streamer.filter(locations=region, languages=['es'], track=track)


def main():
    # Parametros de busqueda #
    search_words = get_keywords()

    # Get Tweets #
    read_tweets(config.region_CHILE, search_words)


if __name__ == "__main__":
    main()
