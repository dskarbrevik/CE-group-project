import boto3
from boto3.dynamodb.conditions import Attr,Key
from botocore.exceptions import ClientError
import tweepy
import os
import sys
import time
from decimal import Decimal
from datetime import date,datetime,timedelta
import traceback

class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self,
                 max_tweets_per_second,
                 tweet_ttl,
                 dynamo_table_name,
                 dynamo_region,
                 sns_error_topic=None,
                 sns_region=None):
        super(TwitterStreamListener, self).__init__()

        self.error_count = 0 # to help with restarting stream smoothly on error
        self.tweet_ttl = tweet_ttl

        # SNS notifications
        self.sns_error_topic = sns_error_topic
        if self.sns_error_topic:
            self.sns = boto3.resource('sns', region_name=sns_region)
            self.topic = self.sns.Topic(sns_error_topic)

        # Dynamo table for storing raw tweets
        self.dynamo = boto3.resource('dynamodb', region_name=dynamo_region)
        self.raw_tweet_table = self.dynamo.Table(dynamo_table_name)

        # rate limiting the Twitter stream to avoid heavy spending on downstream AWS services
        self.max_tweets_per_second = max_tweets_per_second
        self.curr_tweet_count = 0
        self.curr_second = datetime.now()+timedelta(seconds=2)

    # rate limiting the twitter stream
    def check_rate_limit(self):
        if self.curr_second > datetime.now():
            if self.curr_tweet_count < self.max_tweets_per_second:
                return False
            else:
                return True
        else:
            self.curr_second = datetime.now()+timedelta(seconds=2)
            self.curr_tweet_count = 1
            return False

    def on_status(self, status):
        try:
            tweet = status.__dict__['_json']
            if tweet.get('lang',None)=='en':
                tweet['text'] = tweet['text'].lower()
                tweet['time_tl'] = time.time()+self.tweet_ttl
                self.curr_tweet_count += 1
                limited = self.check_rate_limit()
                if not limited:
                    self.raw_tweet_table.put_item(Item=tweet)

            self.error_count = 0
        except Exception as e:
            print(traceback.print_exc())
            self.error_count += 1
            if self.error_count > 3:
                print("Hit three errors. Exiting.")
                if self.sns_error_topic:
                    self.topic.publish(Message=f"Hit 3 errors in a row in on_status\nScraper shutdown time = {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}")
                sys.exit()

    def on_error(self, status_code):
        if status_code == 420 or status_code==429:
            #returning False in on_error disconnects the stream
            self.error_count += 1
            if self.error_count > 3:
                if self.sns_error_topic:
                    self.topic.publish(Message=f"Had to retry 3 times\nStatus code = {status_code}\nScraper shutdown time = {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}")
                sys.exit()
            print(f"Hit https error, retry number at {self.retry_connect}")
            time.sleep(30*(2**self.retry_connect))
            return True

        # returning non-False reconnects the stream, with backoff.
