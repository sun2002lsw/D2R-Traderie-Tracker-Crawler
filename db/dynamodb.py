import boto3
from typing import Dict, Any


class DynamoDB:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('D2R-Traderie-Trades')
    
    def test_connection(self):
        self.table.load()
    
    def put_items(self, items: Dict[str, Any]):
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
