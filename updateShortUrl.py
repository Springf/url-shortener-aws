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
    print('myevent')
    print(event)
    result = ''
    if event['body']:
        body = json.loads(event['body'])
        url =body['url']
        user = body['user']
        short_url = body['short_url']
        if not short_url.lower().startswith('http://') or len(short_url) < len(host):
            result = 'Invalid short URL'
        if short_url == url:
            result = 'Cannot redirect to self.'
        short_url = short_url[-8:]
        try:
            s = Shortener(hash_shortener.shorten, DynamoDBStroe(table), regex_validator.validate)
            if s.update(short_url, url, user):
                result = 'URL updated successfully'
            else: 
                result = 'Cannot Update: either short URL does not exist or you are not the creator of the URL.'
        except ValueError as e:
            result = str(e)
    
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin': f'{host}', 'Content-Type': 'text/html; charset=utf-8'},
        'body': f'{result}'
    }
