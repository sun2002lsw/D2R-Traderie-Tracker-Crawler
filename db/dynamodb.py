import boto3

from .common import TABLE_NAME, BaseDatabase


class DynamoDB(BaseDatabase):
    def _connect(self):
        # 환경변수로 AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY가 자동 적용됨
        db = boto3.resource("dynamodb", region_name="ap-northeast-2")
        self.table = db.Table(TABLE_NAME)
        self._print_connection(self.__class__.__name__)

    def _scan_items(self) -> list:
        response = self.table.scan(
            ProjectionExpression="item_name, update_time",
            Select="SPECIFIC_ATTRIBUTES",
        )

        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = self.table.scan(
                ProjectionExpression="item_name, update_time",
                Select="SPECIFIC_ATTRIBUTES",
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))

        return items

    def _save_item(self, item_data: dict):
        self.table.put_item(Item=item_data)
