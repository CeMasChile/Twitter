# coding: utf-8
# !/usr/bin/env python

import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import tweepy

from datetime import datetime


# read keys ignoring the last char in file: \n.
with open('./keys.txt') as f:
    consumer_key = f.readline()[:-1]
    consumer_secret = f.readline()[:-1]
    access_key = f.readline()[:-1]
    access_secret = f.readline()[:-1]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# parameters
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
MAX_NTWEETS = 1000

LOAD_TWEETS = True


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def main():
    filename_news = "biobio.json"
    keyword_news = "militar"
    news_time = news_data(filename_news, keyword_news)

    # keyword_tweets = '#piñerarenuncia'
    keyword_tweets = '#PiñeraRenuncia'
    since = "2019-10-20"
    until = "2019-10-23"
    if(LOAD_TWEETS is True):
        tweets_text, tweets_dates, tweets_time = \
            load_tweets_data("tweets_%s_%s_%s.npy" % (keyword_tweets, since, until))
    else:
        tweets_text, tweets_dates, tweets_time = \
            tweets_data(keyword_tweets, since=since, until=until, num=MAX_NTWEETS,
                        savename="tweets_%s_%s_%s" % (keyword_tweets, since, until))

    plot_trends(tweets_time, news_time,
                title="Uso de %s en Twitter" % keyword_tweets,
                label_vline="Titular con \"%s\"" % keyword_news)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# functions
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def plot_trends(tweets_t, news_t, title=None, label_vline=None,
                filename="trends"):
    """Plot histogram with tweets time and vertical lines to denote news publications.

    Parameters:
        tweets_t (int[:]): publication time of tweets since epoch
        news_t (int[:]): time of news since epoch
    """
    # formating variables
    xlim = [np.min(tweets_t), np.max(tweets_t)]

    xticks = np.linspace(xlim[0], xlim[1], num=6)
    xticks_labels = ["" for _ in xticks]
    for i in range(1, len(xticks)):
        xticks_labels[i] = datetime.utcfromtimestamp(xticks[i]).strftime('%Y-%m-%d %H:%M')

    # plot
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.hist(tweets_t, bins=np.unique(tweets_t).shape[0], color="darkblue",
            edgecolor='black', linewidth=0.5)
    if(label_vline is None):
        ax.axvline(news_t[0], color="red")
    else:
        ax.axvline(news_t[0], color="red", label=label_vline)
    for t in news_t[1:]:
        ax.axvline(t, color="red")

    ax.set_xlim(xlim)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks_labels, rotation=25, ha="right")

    ax.set_title(title, fontsize=18)
    ax.set_ylabel("Numero de Tweets", fontsize=15)

    if(label_vline is not None):
        ax.legend()
    fig.tight_layout()
    fig.savefig("%s.png" % filename)

    plt.show()
    plt.close(fig)


def load_tweets_data(filename):
    data = np.load(filename)

    tweets_text = list(data[0])
    tweets_dates = list(data[1])
    tweets_t = list(data[2])

    return tweets_text, tweets_dates, tweets_t


def tweets_data(keyword, since=None, until=None, num=None, savename=None):
    """Extract tweets with a certain keyword.

    Parameters:
        keyword (str): string that must be contained in the tweet
        since (str): date from which it will search tweets.  Must be in format year-month-day.
        until (str): date until it which it will search tweets.  Must be in format year-month-day.
        num (int): maximum number of tweets that will be downloaded.
        savename (str): name of the file in which the returns will be saved

    Returns:
        text_arr (str[:]): text content of the tweet.
        date_arr (str[:]): publication date of the tweets.
        time_arr (int[:]): publication time of the tweets since epoch
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    tweets = tweepy.Cursor(api.search, q=keyword, lang='es', since=since, until=until).items(num)

    text_arr = [None for _ in range(num)]
    date_arr = [None for _ in range(num)]
    time_arr = [None for _ in range(num)]
    for n, tweet in enumerate(tweets):
        text_arr[n] = tweet.text

        date = tweet.created_at
        date_arr[n] = date
        time_arr[n] = datetime(date.year, date.month, date.day, date.hour, date.minute).timestamp()

    data = (text_arr[:n+1], date_arr[:n+1], time_arr[:n+1])
    if(savename is not None):
        np.save("%s.npy" % savename, data)

    return data


def news_data(filename, keyword):
    """Extract publication time from news database.

    Parameters:
        filename (str): json filename with news article data.
        keyword (str): string that must be contained in the news' title.

    Returns:
        time_arr (int[:]): time of the news since epoch
    """
    news_arr = None
    with open(filename) as json_file:
        news_arr = json.load(json_file)

    n = 0
    time_arr = [None for _ in range(len(news_arr))]
    for i, news in enumerate(news_arr):
        if(keyword in news["title"]):
            date = "%s %s" % (news["publication_date"][1:], news["publication_hour"])
            date = datetime.strptime(date, '%d/%m/%Y %H:%M')
            time_arr[n] = date.timestamp()

            n += 1

    return time_arr[:n]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
if __name__ == '__main__':
    main()
