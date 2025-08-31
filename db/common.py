import json
from abc import ABC, abstractmethod
from datetime import datetime

from helper.log import log_print

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class BaseDatabase(ABC):
    def __init__(self):
        self._connect()
        log_print(f"{self.__class__.__name__} 연결")

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
        for item in items:
            log_print(f"{item['item_name']} - {item['update_time']}")

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
