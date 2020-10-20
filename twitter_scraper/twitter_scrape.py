from tweepy_listener import TwitterStreamListener
import tweepy
import json
import os
import boto3
from datetime import datetime, timedelta
import time
import traceback
import sys

if __name__=='__main__':


    # setup credentials and terms to track
    with open('./config.json','rb') as file:
        config = json.load(file)

    consumer_key = config['twitter_credentials']['consumer_key']
    consumer_secret = config['twitter_credentials']['consumer_secret']
    access_token = config['twitter_credentials']['access_token']
    access_token_secret = config['twitter_credentials']['access_token_secret']

    # sns = boto3.resource(service_name='sns',region_name='us-east-1')
    # topic = sns.Topic(config['sns_error_topic'])
    # # setup twitter stream
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    error_count = 0
    last_error_time = datetime.now()

    terms = config['twitter_terms']

    print(f"Starting Twitter stream to track the following terms: {terms}")
    while True:
        try:
            stream_listener = TwitterStreamListener(max_tweets_per_second=config['max_tweets_per_second'],
                                                    tweet_ttl=config['tweet_ttl'],
                                                    dynamo_table_name=config['dynamo_table_name'],
                                                    dynamo_region=config['dynamo_region'],
                                                    sns_error_topic=config['sns_error_topic_arn'])
            stream = tweepy.Stream(auth=api.auth,
                                   listener=stream_listener)
            stream.filter(track=terms)
        except Exception as e:
            error_time = datetime.now()
            diff = error_time - last_error_time
            if diff < timedelta(minutes=5):
                error_count+=1
            else:
                error_count=1
            last_error_time = error_time
            if error_count > 3:
                print("Hit three errors.")
                # topic.publish(Message=f"Hit error.\nError Count = {error_count}\nError = {traceback.print_exc()}\nError time = {datetime.now().strftime('%m/%d/%Y %H:%M:%S')}")
                sys.exit()
            else:
                print(e)
                time.sleep(60)
                print("\nRetrying Twitter stream connection...")
