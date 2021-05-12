from core.api import Shortener
from core.shortener import hash_shortener
from core.validator import regex_validator
from store.dynamodb_store import DynamoDBStroe
import boto3
import json
dynamo = boto3.resource('dynamodb')
table = 'url_store'
host = 'https://www.sggti.net'

def lambda_handler(event, context):
    """
    lambda function to call the shortener core api to create the shortened string
    """
    print('Received event:')
    print(event)
    result = ''
    if event['body']:
        body = json.loads(event['body'])
        url =body['url']
        user = body['user']
        s = Shortener(hash_shortener.shorten, DynamoDBStroe(table), regex_validator.validate)
        try:
            result = f"{host}/{s.create(url, user)}"
        except ValueError as e:
            result = str(e)
    else:
        result = 'Error creating short URL: bad input.'

    return {
        'statusCode': 200,
        'headers': { 'Content-Type': 'text/html; charset=utf-8'},
        'body': f'{result}'
    }
