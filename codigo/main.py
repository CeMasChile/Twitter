import os
import csv
import tweepy
import pandas as pd








# Primero nos autenticamos en twitter

with open('./keys.txt') as f:
    consumer_key = f.readline()[:-1]
    consumer_secret = f.readline()[:-1]
    access_key = f.readline()[:-1]
    access_secret = f.readline()[:-1]
    f.close()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

# creamos un objeto API

api = tweepy.API(auth)


# Abrimos las keywords en una lista de python

with open('./kw.csv', 'r') as f:
    reader = csv.reader(f)
    keywords = list(reader)[0]

# limpiamos los espacios
for i in range(len(keywords)):
    if keywords[i][0] == ' ':
        keywords[i] = keywords[i][1::]

# Queremos buscar t0do lo que tenga alguna palabra que aparezca en la lista de keywords

search_words = ' OR '.join(keywords[:9])
date_since = "2019-10-16"


tweets = tweepy.Cursor(api.search,
                       q=search_words,
                       lang='es',
                       since=date_since).items(500)


tweets_list = [tweet for tweet in tweets]


users_locs = [[h.user.screen_name, h.user.location] for h in tweets_list]


# Se crea un DataFrame de Pandas

tweet_text = pd.DataFrame(data=users_locs,
                    columns=['user', "location"])

