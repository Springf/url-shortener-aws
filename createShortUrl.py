from core.api import Shortener
from core.shortener import hash_shortener
from core.validator import regex_validator
from store.dynamodb_store import DynamoDBStroe
import boto3
dynamo = boto3.resource('dynamodb')
table = 'url_store'
host = 'https://www.sggti.net'

def lambda_handler(event, context):
    print('myevent')
    print(event)
    result = ''
    if event['body']:
        url = event['body']['url']
        user = event['body']['user']
        s = Shortener(hash_shortener.shorten, DynamoDBStroe(table), regex_validator.validate)
        try:
            result = f"{host}{s.create(url, user)}"
        except ValueError as e:
            result = str(e)
    
    return {
        'statusCode': 200,
        'headers': { 'Access-Control-Allow-Origin': f'{host}', 'Content-Type': 'text/html; charset=utf-8'},
        'body': f'{result}'
    }
