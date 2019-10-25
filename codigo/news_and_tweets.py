# coding: utf-8
# !/usr/bin/env python

import csv
import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import tweepy as tw

from datetime import datetime


# read keys ignoring the last char in file: \n.
with open('./keys.txt') as f:
    consumer_key = f.readline()[:-1]
    consumer_secret = f.readline()[:-1]
    access_key = f.readline()[:-1]
    access_secret = f.readline()[:-1]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def main():
    filename_news = "biobio.json"
    keyword_news = "militar"
    news_t = news_time(filename_news, keyword_news)

    # keyword_tweets = '#piñerarenuncia'
    keyword_tweets = '#PiñeraRenuncia'
    since = "2019-10-20"
    until = "2019-10-23"
    tweets_text, tweets_dates, tweets_t = \
        tweets_time(keyword_tweets, since=since, until=until, num=10)

    plot_trends(news_t, tweets_t)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# functions
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def plot_trends(tweets_t, news_t, filename="trends"):
    """Plot histogram with tweets time and vertical lines to denote news publications.

    Parameters:
        tweets_t (int[:]): publication time of tweets since epoch
        news_t (int[:]): time of news since epoch
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.hist(tweets_t, color="darkblue")
    for t in news_t:
        ax.axvline(t, color="red")

    ax.set_xlim([np.min(tweets_t), np.max(tweets_t)])

    fig.tight_layout()
    fig.savefig("%s.png" % filename)

    plt.show()
    plt.close(fig)


def tweets_time(keyword, since=None, until=None, num=None, savename=None):
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
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tw.API(auth, wait_on_rate_limit=True)

    tweets = tw.Cursor(api.search, q=keyword, lang='es', since=since, until=until).items(num)

    text_arr = [None for _ in range(num)]
    date_arr = [None for _ in range(num)]
    time_arr = [None for _ in range(num)]
    for n, tweet in enumerate(tweets):
        text_arr[n] = tweet.text

        date = tweet.created_at
        date_arr[n] = date
        time_arr[n] = datetime(date.year, date.month, date.day, date.hour, date.minute).timestamp()

    data = text_arr[:n], date_arr[:n], time_arr[:n]
    if(savename is not None):
        np.save(savename, data)

    return data


def news_time(filename, keyword):
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
