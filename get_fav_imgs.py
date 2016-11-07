#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import hashlib
import re
import ConfigParser
import requests
import tweepy
from tweepy.error import TweepError

def md5sum(data):
    return hashlib.md5(data).hexdigest()


def download_images(urls, save_dir):
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if urls:
        for url in urls:
            r = requests.get(url, verify=False)
            mExtension = re.match(r'.*([.].*)$', url)
            if not mExtension:
                continue
            extension = mExtension.group(1)
            fname = md5sum(r.content) + extension
            with open(os.path.join(save_dir, fname), 'wb') as f:
                f.write(r.content)


class TwitterCrawler:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.api = None
        self.img_urls = []

    def setup(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)

    def get_fav_image_urls(self, user_id, num_of_page):
        for x in xrange(num_of_page):
            try:
                fav_tweets = self.api.favorites(user_id, page=x+1)
            except TweepError:
                # Hit rate limit :(
                break
            for i, tweet in enumerate(fav_tweets):
                json_data = tweet._json
                try:
                    image_url = json_data['extended_entities']['media'][0]['media_url']
                except KeyError:
                    continue
                self.img_urls.append(image_url)

    def show_fav_image_urls(self):
        for img_url in self.img_urls:
            print img_url


def main():
    conf = ConfigParser.SafeConfigParser()
    conf.read('./config.ini')

    consumer_key = conf.get('twitter', 'consumer_key')
    consumer_secret = conf.get('twitter', 'consumer_secret')
    access_token = conf.get('twitter', 'access_token')
    access_token_secret = conf.get('twitter', 'access_token_secret')
    target_twitter_id = conf.get('twitter', 'target_twitter_id')
    save_dir = conf.get('twitter', 'save_dir')

    tw_crawler = TwitterCrawler(consumer_key, consumer_secret, access_token, access_token_secret)
    tw_crawler.setup()
    tw_crawler.get_fav_image_urls(target_twitter_id, 10) # Check (10 * 20) tweet
    tw_crawler.show_fav_image_urls()
    download_images(tw_crawler.img_urls, save_dir)


if __name__ == '__main__':
    main()
