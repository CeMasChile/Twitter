import sys
sys.path.append(sys.prefix.replace('/env', '')) # esto es pa importar utils y config
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy import http
from scrapy.shell import inspect_response  # for debugging
import re
import json
import time
import logging
import tweepy
import config
from lxml import html
from utils import extract_hash_tags
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

from datetime import datetime

from TweetScraper.items import Tweet, User

logger = logging.getLogger(__name__)

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


class TweetScraper(CrawlSpider):
    name = 'TweetScraper'
    allowed_domains = ['twitter.com']

    def __init__(self, query='', lang='', crawl_user=False, top_tweet=False):

        self.query = query
        self.url = "https://twitter.com/i/search/timeline?l={}".format(lang)

        if not top_tweet:
            self.url = self.url + "&f=tweets"

        self.url = self.url + "&q=%s&src=typed&max_position=%s"

        self.crawl_user = crawl_user

    def start_requests(self):
        url = self.url % (quote(self.query), '')
        yield http.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        # inspect_response(response, self)
        # handle current page
        data = json.loads(response.body.decode("utf-8"))
        for item in self.parse_tweets_block(data['items_html']):
            yield item

        # get next page
        min_position = data['min_position']
        min_position = min_position.replace("+","%2B")
        url = self.url % (quote(self.query), min_position)
        yield http.Request(url, callback=self.parse_page)

    def parse_tweets_block(self, html_page):
        page = Selector(text=html_page)

        ### for text only tweets
        items = page.xpath('//li[@data-item-type="tweet"]/div')
        for item in self.parse_tweet_item(items):
            yield item

    def parse_tweet_item(self, items):
        for item in items:
            try:
                tweet = Tweet()

                tweet['usernameTweet'] = item.xpath('.//span[@class="username u-dir u-textTruncate"]/b/text()').extract()[0]

                ID = item.xpath('.//@data-tweet-id').extract()
                if not ID:
                    continue
                tweet['ID'] = ID[0]

                ### get text content
#                tweet['text'] = ' '.join(
#                    item.xpath('.//div[@class="js-tweet-text-container"]/p//text()|.//div[@class="js-tweet-text-container"]/p//img/@alt').extract()).replace(' # ',
#                                                                                                        '#').replace(
#                    ' @ ', '@')
                p_txt=item.xpath('.//div[@class="js-tweet-text-container"]/p').extract()
                p_txt=" ".join(p_txt)
                p = html.fromstring(p_txt)
                a_links=p.xpath("//p/a")
                for a in a_links:
                    if 'twitter-atreply' in a.attrib['class']:
                        # for getting @xyz mentions
                        txt = "@" + a.attrib['href'].split("/")[1]
                        for child in list(a):
                            a.remove(child)
                        a.text = txt
                    elif 'twitter-hashtag' in a.attrib['class']:
                        # for getting #xyz hashtag
                        txt = "#" + a.attrib['href'].split("?")[0].split("/")[2]
                        for child in list(a):
                            a.remove(child)
                        a.text = txt
                    elif 'twitter-timeline-link u-hidden' in a.attrib['class']:
                        # For removing pic.twitter.... link that sometimes comes up in the bottom of a tweet
                        for child in list(a):
                            a.remove(child)
                        a.text = ""
                    elif 'twitter-timeline-link' in a.attrib['class'] and 'data-expanded-url' in a.attrib:
                        # for getting embedding links of type http[s]://xyz.com
                        txt = a.attrib['data-expanded-url']
                        for child in list(a):
                            a.remove(child)
                        a.text = txt
                text=p.xpath("//p//text()")
                tweet['text'] = ' '.join(text)
                if tweet['text'] == '':
                    # If there is not text, we ignore the tweet
                    continue

                ### get meta data
                tweet['url'] = item.xpath('.//@data-permalink-path').extract()[0]

                nbr_retweet = item.css('span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount').xpath(
                    '@data-tweet-stat-count').extract()
                if nbr_retweet:
                    tweet['nbr_retweet'] = int(nbr_retweet[0])
                else:
                    tweet['nbr_retweet'] = 0

                nbr_favorite = item.css('span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount').xpath(
                    '@data-tweet-stat-count').extract()
                if nbr_favorite:
                    tweet['nbr_favorite'] = int(nbr_favorite[0])
                else:
                    tweet['nbr_favorite'] = 0

                nbr_reply = item.css('span.ProfileTweet-action--reply > span.ProfileTweet-actionCount').xpath(
                    '@data-tweet-stat-count').extract()
                if nbr_reply:
                    tweet['nbr_reply'] = int(nbr_reply[0])
                else:
                    tweet['nbr_reply'] = 0

                tweet['datetime'] = datetime.fromtimestamp(int(
                    item.xpath('.//div[@class="stream-item-header"]/small[@class="time"]/a/span/@data-time').extract()[
                        0])).strftime('%Y-%m-%d %H:%M:%S')

                ### get photo
                has_cards = item.xpath('.//@data-card-type').extract()
                if has_cards and has_cards[0] == 'photo':
                    tweet['has_image'] = True
                    tweet['images'] = item.xpath('.//*/div/@data-image-url').extract()
                elif has_cards:
                    logger.debug('Not handle "data-card-type":\n%s' % item.xpath('.').extract()[0])

                ### get animated_gif
                has_cards = item.xpath('.//@data-card2-type').extract()
                if has_cards:
                    if has_cards[0] == 'animated_gif':
                        tweet['has_video'] = True
                        tweet['videos'] = item.xpath('.//*/source/@video-src').extract()
                    elif has_cards[0] == 'player':
                        tweet['has_media'] = True
                        tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
                    elif has_cards[0] == 'summary_large_image':
                        tweet['has_media'] = True
                        tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
                    elif has_cards[0] == 'amplify':
                        tweet['has_media'] = True
                        tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
                    elif has_cards[0] == 'summary':
                        tweet['has_media'] = True
                        tweet['medias'] = item.xpath('.//*/div/@data-card-url').extract()
                    elif has_cards[0] == '__entity_video':
                        pass  # TODO
                        # tweet['has_media'] = True
                        # tweet['medias'] = item.xpath('.//*/div/@data-src').extract()
                    else:  # there are many other types of card2 !!!!
                        logger.debug('Not handle "data-card2-type":\n%s' % item.xpath('.').extract()[0])

                is_reply = item.xpath('.//div[@class="ReplyingToContextBelowAuthor"]').extract()
                tweet['is_reply'] = is_reply != []

                is_retweet = item.xpath('.//span[@class="js-retweet-text"]').extract()
                tweet['is_retweet'] = is_retweet != []

                tweet['user_id'] = item.xpath('.//@data-user-id').extract()[0]

                tweet['hash_tags'] = extract_hash_tags(text)

                yield tweet

                if self.crawl_user:
                    ### get user info
                    user = User()
                    twuser = api.get_user(user_id = tweet['user_id'])
                    user['user_id'] = twuser.id
                    user['name'] = twuser.name
                    user['screen_name'] = twuser.screen_name
                    user['description'] = twuser.description
                    user['created_at'] = twuser.created_at
                    user['follower_count'] = twuser.follower_count
                    user['statuses_count'] = twuser.statuses_count
                    user['verified'] = twuser.verified
                    user['location'] = twuser.location
                    user['geo_enabled'] = twuser.geo_enabled
                    user['url'] = twuser.url
                    yield user
            except:
                logger.error("Error tweet:\n%s" % item.xpath('.').extract()[0])
                # raise

    def extract_one(self, selector, xpath, default=None):
        extracted = selector.xpath(xpath).extract()
        if extracted:
            return extracted[0]
        return default
