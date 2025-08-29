import json
import os

import db
import traderie
import webdriver


def main():
    print("===== 웹 드라이버 생성 시작 =====")
    chrome_driver = webdriver.StealthDriver()
    driver = chrome_driver.get_driver()
    print("===== 웹 드라이버 생성 완료 =====\n")

    with open("traderie/traderie_items.json", "r", encoding="utf-8") as f:
        traderie_items = set(json.load(f))

    if os.getenv("Develop") != "true":
        print("===== DB 데이터 조회 시작 =====")
        db_instance = db.CloudFirestore()
        items = db_instance.get_items()
        db_items = set(item["item_name"] for item in items)

        not_in_db_items = [
            item for item in traderie_items if item not in db_items
        ]

        if not_in_db_items:
            target_item_name = not_in_db_items[0]
        else:
            oldest_item_info = min(items, key=lambda x: x["update_time"])
            target_item_name = oldest_item_info["item_name"]
        print("===== DB 데이터 조회 완료 =====\n")
    else:
        target_item_name = next(iter(traderie_items))

    print("===== 크롤링 시작 =====")
    crawler = traderie.Crawler(driver)
    trade_list = crawler.crawl_trade_list(target_item_name)
    print("===== 크롤링 완료 =====\n")

    if os.getenv("Develop") != "true":
        print("===== DB 데이터 삽입 시작 =====")
        db_instance.put_item(target_item_name, trade_list)
        print("===== DB 데이터 삽입 완료 =====\n")


if __name__ == "__main__":
    print("\n")  # 그냥 빈줄용
    main()
