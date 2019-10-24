import csv
import tweepy
import pandas as pd
import config


def get_keywords():
    # Abrimos las keywords en una lista de python
    with open('./kw.csv', 'r') as f:
        reader = csv.reader(f)
        keywords = list(reader)[0]

    # limpiamos los espacios
    for i in range(len(keywords)):
        if keywords[i][0] == ' ':
            keywords[i] = keywords[i][1::]

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
if __name__ == '__main__':
    main()
