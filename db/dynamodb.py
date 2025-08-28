import boto3
import os
from datetime import datetime


class DynamoDB:
    def __init__(self):
        if os.getenv('LOCAL_DEV'):
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url='http://localhost:4566',
                region_name='ap-northeast-2',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
            print("LocalStack DynamoDB에 연결")
        else:
            self.dynamodb = boto3.resource('dynamodb')
            print("AWS DynamoDB에 연결")
        
        self.table = self.dynamodb.Table('D2R-Traderie-Trades')
    
    def get_item_infos(self):
        response = self.table.scan(
            ProjectionExpression='item_name, update_time',
            Select='SPECIFIC_ATTRIBUTES'
        )
        items = response.get('Items', [])
        
        # 페이지네이션 처리
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                ProjectionExpression='item_name, update_time',
                Select='SPECIFIC_ATTRIBUTES',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
        
        print(f"아이템 정보 조회 완료")
        for item in items:
            print(f"{item['item_name']} - {item['update_time']}")
            
        return items
    
    def put_item(self, item_name: str, trade_list: list):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.table.put_item(Item={
            'item_name': item_name,
            'update_time': current_time,
            'trade_list': trade_list
        })
        
        print(f"{item_name} 아이템 업데이트 완료 - {current_time}")
    