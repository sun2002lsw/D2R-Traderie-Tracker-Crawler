import json
from abc import ABC, abstractmethod
from datetime import datetime

TABLE_NAME = "d2r-traderie-trades"
TIME_FORMAT = "%Y-%m-%d %H:%M"


class BaseDatabase(ABC):
    def __init__(self):
        self.table = None
        self._connect()
        print(f"{self.__class__.__name__} 연결")

    @abstractmethod
    def _connect(self):
        pass

    @abstractmethod
    def _get_items_impl(self) -> list:
        pass

    @abstractmethod
    def _put_item_impl(self, item_data: dict):
        pass

    def get_items(self) -> list:
        items = self._get_items_impl()

        print("아이템 정보 조회 완료")
        for item in items:
            print(f"{item['item_name']} - {item['update_time']}")

        return items

    def put_item(self, item_name: str, trade_list: list):
        current_time = datetime.now().strftime(TIME_FORMAT)
        trade_list_json = json.dumps(trade_list, ensure_ascii=False)

        item_data = {
            "item_name": item_name,
            "update_time": current_time,
            "trade_list": trade_list_json,
        }

        self._put_item_impl(item_data)

        print(f"{item_name} 아이템 업데이트 완료 - {current_time}")
        print(f"{trade_list_json}")
