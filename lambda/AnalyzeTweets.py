import json
import boto3
import os

def update_table(table, data):

    key = {'id':data['key']}
    update_expression = "set info.rating=:r, info.plot=:p, info.actors=:a"
    expression_attributes = {
        ':r': Decimal(rating),
        ':p': plot,
        ':a': actors
    }

    response = table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attributes)


def lambda_handler(event, context):
    print(os.environ)
    comprehend = boto3.client('comprehend')
    dynamodb = boto3.resource('dynamodb', region_name=os.environ['dynamo_region'])
    table = dynamodb.Table(os.environ['dynamo_table_name'])

    for record in event['Records']:
        tweet = record['dynamodb']['NewImage']['text']
        response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
        sentiment = response['Sentiment']

        print(response['Sentiment'])

        if response['Sentiment']=='POSITIVE':
            data ={}
        elif response['Sentiment']=='NEGATIVE':
            data =

        POSITIVE'|'NEGATIVE'|'NEUTRAL'|'MIXED'
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
