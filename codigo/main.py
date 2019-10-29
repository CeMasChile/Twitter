import csv

import pandas as pd
import tweepy
import io
import config


def get_keywords():
    """
    Returns a Python list of strings read from the file kw.csv'
    """
    # Abrimos las keywords como string
    keywordfile = io.open('./kw.csv').read()

    #Convertimos a lista de Python
    keywords = keywordfile.split(', ')
    return keywords


def get_searchWords():
    # Queremos buscar t0do lo que tenga alguna palabra que aparezca en la lista de keywords
    keywords = get_keywords()
    return ' OR '.join(keywords[:9])


def main():
    # AUTH #
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    # API #
    api = tweepy.API(auth)

    # Parametros de busqueda #
    search_words = get_searchWords()
    date_since = "2019-10-16"

    # CURSOR #
    tweets = tweepy.Cursor(api.search,
                           q=search_words,
                           lang='es',
                           since=date_since).items(500)

    # PROCESSING #
    tweets_list = [tweet for tweet in tweets]

    users_locs = [[h.user.screen_name, h.user.location] for h in tweets_list]

    # DATAFRAME #
    tweet_text = pd.DataFrame(data=users_locs,
                              columns=['user', "location"])
    return tweet_text


if __name__ == '__main__':
    main()

'''
# drop non located tweets
df = tweet_text.copy()
df['location'].replace('', np.nan, inplace=True)
df.dropna(subset=['location'], inplace=True)
df
'''
