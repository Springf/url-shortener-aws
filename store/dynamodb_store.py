from core.store.store import Store
import boto3
from botocore.exceptions import ClientError

class DynamoDBStroe(Store):
    def __init__(self, table) -> None:
        super().__init__()
        self.__store = boto3.client('dynamodb')
        self.__url_key = 'url'
        self.__user_key = 'user'
        self.__table = table
        self.__partition_key = 'shortened_url'
    
    def add(self, short_url:str, url:str, user:str = None) -> bool:
        if not short_url or not url:
            raise ValueError('URL cannot be empty.')
        if user is None:
            user = ''
        item={
            self.__partition_key:{'S': short_url},
            self.__url_key:{'S': url},
            self.__user_key:{'S': user}
        }
        try:
            self.__store.put_item(TableName = self.__table, Item=item, ConditionExpression=f'attribute_not_exists({self.__partition_key})')
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(e.response['Error']['Message'])
                existing_url = self.__store.get_item(TableName = self.__table, AttributesToGet = [self.__url_key], Key= { self.__partition_key : { 'S': short_url}})
                return url == existing_url['Item'][self.__url_key]['S']
            else:
                raise

    def get(self, short_url:str) -> str:
        if not short_url:
            raise ValueError('URL cannot be empty.')
        item = self.__store.get_item(TableName = self.__table, AttributesToGet = [self.__url_key], Key= { self.__partition_key : { 'S': short_url}})
        if 'Item' in item:
            return item['Item'][self.__url_key]['S']
        return None
    
    def update(self, short_url:str, url:str, user:str) -> bool:
        if not short_url or not url or not user:
            raise ValueError('URL or user cannot be empty.')
        item = self.__store.get_item(TableName = self.__table, AttributesToGet = [self.__url_key, self.__user_key], Key= { self.__partition_key : { 'S': short_url}})
        if 'Item' in item:
            print(item)
            print('abc')
            if user != item['Item'][self.__user_key]['S']:
                return False
            else:
                item={
                    self.__partition_key:{'S': short_url},
                    self.__url_key:{'S': url},
                    self.__user_key:{'S': user}
                }
                self.__store.put_item(TableName = self.__table, Item=item)
                return True
        else:
            return False
