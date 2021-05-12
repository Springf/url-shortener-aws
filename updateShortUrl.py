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
    lambda function to call the shortener core api to update an existing shortened string's original URL to a new URL.
    """
    print('Received event:')
    print(event)
    result = ''
    if event['body']:
        body = json.loads(event['body'])
        url =body['url']
        user = body['user']
        short_url = body['short_url']
        
        #some minimum validation
        if not short_url.lower().startswith(host):
            result = 'Invalid short URL'
        if short_url == url:
            result = 'Cannot redirect to self.'
        #get the shortened string only as core api expects no domain name
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
        'headers': {  'Content-Type': 'text/html; charset=utf-8'},
        'body': f'{result}'
    }
