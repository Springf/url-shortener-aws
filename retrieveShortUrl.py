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
    lambda function to call the shortener core api to retrieve the original URL based on shortened string.
    return 302 redirect to the caller.
    """
    print('Received event:')
    print(event)
    result = 'error.html'
    
    if event['pathParameters']:
        shorturl = event['pathParameters']['shorturl']
        s = Shortener(hash_shortener.shorten, DynamoDBStroe(table), regex_validator.validate)
        try:
            result = s.retrieve(shorturl)
        except ValueError:
            result = 'error.html'
    
    return {
        'statusCode': 302,
        'headers': { 'Location': f'{result}'}
    }
