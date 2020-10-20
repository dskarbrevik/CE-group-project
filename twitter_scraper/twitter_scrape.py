from tweepy_listener import TwitterStreamListener
import tweepy
import json
import os
import boto3
from datetime import datetime, timedelta
import time
import traceback
import sys
import base64
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "twitter-credentials"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            
        return(decoded_binary_secret)

if __name__=='__main__':


    twitter_credentials = get_secret()

    consumer_key = twitter_credentials['twitter_consumer_key']
    consumer_secret = twitter_credentials['twitter_consumer_secret']
    access_token = twitter_credentials['twitter_access_token']
    access_token_secret = twitter_credentials['twitter_access_token_secret']

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
