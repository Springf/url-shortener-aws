from store.dynamodb_store import DynamoDBStroe
import pytest
import boto3
dynamo = boto3.resource('dynamodb')
table = 'url_test_store'

def clean(tableName):
    table = dynamo.Table(tableName)
    
    #get the table keys
    tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

    #Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ", ".join('#' + key for key in tableKeyNames)
    expressionAttrNames = {'#'+key: key for key in tableKeyNames}
    
    counter = 0
    page = table.scan(ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames)
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            counter += page["Count"]
            # Delete items in batches
            for itemKeys in page["Items"]:
                batch.delete_item(Key=itemKeys)
            # Fetch the next page
            if 'LastEvaluatedKey' in page:
                page = table.scan(
                    ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames,
                    ExclusiveStartKey=page['LastEvaluatedKey'])
            else:
                break
    print(f"Deleted {counter}") 

def test_add():
    store = DynamoDBStroe(table)
    clean(table)
    assert store.add('short', 'long')
    assert store.add('short1', 'long1')
    assert store.add('short1', 'long1')
    assert store.add('short1', 'long2') == False
    with pytest.raises(ValueError):
        store.add('', '')
    with pytest.raises(ValueError):
        store.add(None, '')

def test_get():
    store = DynamoDBStroe(table)
    clean(table)
    store.add('short', 'long')
    store.add('short1', 'long1')
    store.add('short1', 'longlong')
    store.add('short2', 'long2')

    assert store.get('short') == 'long'
    assert store.get('short1') == 'long1'
    assert store.get('short2') == 'long2'
    assert store.get('short3') is None
    with pytest.raises(ValueError):
        store.get('')
    with pytest.raises(ValueError):
        store.get(None)

def test_update():
    store = DynamoDBStroe(table)
    clean(table)
    assert store.add('short', 'long', 'user')
    assert store.add('short1', 'long1', 'user')
    assert store.add('short1', 'long1', 'user')
    assert store.get('short1') == 'long1'
    assert store.update('short1', 'long2', 'user')
    assert store.get('short1') == 'long2'
    assert store.add('short1', 'longlong') == False
    assert store.update('short', 'longlong', 'user2') == False
    with pytest.raises(ValueError):
        assert store.update('short1', '', '')