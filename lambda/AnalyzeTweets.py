import json
import boto3
import os
from decimal import Decimal
from datetime import datetime
import time

def add_to_table(table, data, time_tl_diff):
    
    key = {'id': datetime.now().strftime("%m-%d-%Y:%H_%M")}
    
    update_expression = f"set {data[0]}={data[0]}+:val1, time_tl=:val2"
    
    expression_attribute_values={':val1':Decimal(data[1]),
                                 ':val2':Decimal(round(time.time())+time_tl_diff)}
    
    table.update_item(Key=key,
                      UpdateExpression=update_expression,
                      ExpressionAttributeValues=expression_attribute_values)

def lambda_handler(event, context):
    terms = ['trump','biden']
    comprehend = boto3.client('comprehend')
    dynamodb = boto3.resource('dynamodb', region_name=os.environ['dynamo_region'])
    table = dynamodb.Table(os.environ['dynamo_table_name'])
    time_tl_diff = int(os.environ['time_tl_diff'])
    record_count = 0
    for record in event['Records']:
        try:
            tweet = record['dynamodb']['NewImage']['text']
            response = comprehend.detect_sentiment(Text=tweet, LanguageCode='en')
            sentiment = response['Sentiment']
            if sentiment=='POSITIVE' or sentiment=='NEGATIVE':
                found_terms = []
                for term in terms:
                    if term in tweet:
                        if term not in found_terms:
                            found_terms.append(term)
                if len(found_terms)==1:
                    add_to_table(table,(f'{term}_{sentiment}',1),time_tl_diff)
                    record_count+=1
        except Exception as e:
            print("Error while parsing through record...\n\n")
            print(str(e))
            

    return {
        'statusCode': 200,
        'body': json.dumps(f'Wrote {record_count} records to new table.')
    }

