import json
import boto3
import os
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import time
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from textblob import TextBlob
import math


def add_to_table(table, data, time_tl_diff):
    timestamp = datetime.now(tz=timezone.utc)
    seconds = int(math.floor(timestamp.second/10)*10)
    timestamp = str(timestamp.replace(second=seconds, microsecond=0))
    
    key = {'id': timestamp}
    
    update_expression = f"set {data[0]}={data[0]}+:val1, time_tl=:val2, {data[2]}={data[2]}+:val3"
    
    expression_attribute_values={':val1':round(Decimal(data[1]),2),
                                 ':val2':Decimal(round(time.time())+time_tl_diff),
                                 ':val3':Decimal(1)}
    print(round(Decimal(data[1]),2))
    try:
        table.update_item(Key=key,
                          UpdateExpression=update_expression,
                          ExpressionAttributeValues=expression_attribute_values,
                          ConditionExpression = Attr(data[0]).exists())
        print("updated table")
    except ClientError as e:
        print(e)
        print("hit an error")
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            update_expression = f"set {data[0]}=:val1, time_tl=:val2, {data[2]}=:val3"
            table.update_item(Key=key,
                              UpdateExpression=update_expression,
                              ExpressionAttributeValues=expression_attribute_values)
            print("updated on error")

def lambda_handler(event, context):
    terms = ['trump','biden']
    dynamodb = boto3.resource('dynamodb', region_name=os.environ['dynamo_region'])
    table = dynamodb.Table(os.environ['dynamo_table_name'])
    time_tl_diff = int(os.environ['time_tl_diff'])
    record_count = 0
    for record in event['Records']:
        try:
            if record['eventName']=='INSERT':
                tweet = record['dynamodb']['NewImage']['text']['S']
                
                # get sentiment
                sentiment_score = TextBlob(tweet).sentiment.polarity

                found_terms = []
                for term in terms:
                    if term in tweet:
                        if term not in found_terms:
                            found_terms.append(term)
                if len(found_terms)==1:
                    add_to_table(table,(f'{found_terms[0]}_sentiment_score',sentiment_score,f'{found_terms[0]}_tweet_count'),time_tl_diff)
                    record_count+=1
        except Exception as e:
            print("Error while parsing through record...\n\n")
            print(str(e))
            
    f'Wrote {record_count} records to new table.'
