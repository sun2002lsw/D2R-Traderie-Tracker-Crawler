import json
import os
from datetime import datetime, timedelta

import db
import traderie
import webdriver
from helper.log import log_print


def run():
    log_print("===== 웹 드라이버 생성 시작 =====")
    chrome_driver = webdriver.StealthDriver()
    driver = chrome_driver.get_driver()
    log_print("===== 웹 드라이버 생성 완료 =====\n")

    db_instance = None
    with open("traderie/traderie_items.json", "r", encoding="utf-8") as f:
        traderie_items = set(json.load(f))

    if os.getenv("Develop") != "true":
        log_print("===== DB 데이터 조회 시작 =====")
        db_instance = db.CloudFirestore()
        items = db_instance.get_items()

        # DB에 없는 아이템들의 이름 추출
        db_items = set(item["item_name"] for item in items)
        target_item_names = [item for item in traderie_items if item not in db_items]

        # 3시간이 지난 아이템들의 이름 추출
        three_hours_ago = datetime.now() - timedelta(hours=3)
        for item in items:
            update_time = datetime.strptime(item["update_time"], db.TIME_FORMAT)
            if update_time < three_hours_ago:
                target_item_names.append(item["item_name"])

        log_print("===== DB 데이터 조회 완료 =====\n")
    else:
        target_item_names = [item for item in traderie_items]

    log_print("===== 크롤링 시작 =====")
    crawler = traderie.Crawler(driver)
    crawler.crawl_trade_list(target_item_names, db_instance)
    log_print("===== 크롤링 완료 =====\n")


if __name__ == "__main__":
    log_print("\n")  # 그냥 빈줄용
    run()
