import boto3
import os
import json
from datetime import datetime


class DynamoDB:
    def __init__(self):
        # 환경변수로 AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY 주입된거 찾아서 접속
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
        self.table = self.dynamodb.Table('D2R-Traderie-Trades')
        print("AWS DynamoDB 연결")  
    
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
        trade_list_json = json.dumps(trade_list, ensure_ascii=False)

        self.table.put_item(Item={
            'item_name': item_name,
            'update_time': current_time,
            'trade_list': trade_list_json
        })
        
        print(f"{item_name} 아이템 업데이트 완료 - {current_time}")
        print(f"{trade_list_json}")
    