import webdriver
import traderie
import json
from db import DynamoDB


def handler(event, context):
    driver = None

    try:
        print("===== 웹 드라이버 생성 시작 =====")
        chrome_driver = webdriver.StealthDriver()
        driver = chrome_driver.get_driver()
        print("===== 웹 드라이버 생성 완료 =====\n")

        print("===== DB 데이터 조회 시작 =====")
        db = DynamoDB()
        items = db.get_items()
        db_items = set(item["item_name"] for item in items)

        with open("traderie/traderie_items.json", "r", encoding="utf-8") as f:
            traderie_items = set(json.load(f))
        not_in_db_items = [item for item in traderie_items if item not in db_items]

        if not_in_db_items:
            target_item_name = not_in_db_items[0]
        else:
            oldest_item_info = min(items, key=lambda x: x["update_time"])
            target_item_name = oldest_item_info["item_name"]
        print("===== DB 데이터 조회 완료 =====\n")

        print("===== 크롤링 시작 =====")
        crawler = traderie.Crawler(driver)
        trade_list = crawler.crawl_trade_list(target_item_name)
        print("===== 크롤링 완료 =====\n")
        
        print("===== DB 데이터 삽입 시작 =====")
        db.put_item(target_item_name, trade_list)
        print("===== DB 데이터 삽입 완료 =====\n")
        
        return {
            "statusCode": 200,
            "body": "success"
        }
        
    except Exception as e:
        error_msg = f"에러 발생: {str(e)}"
        print(error_msg)
        return {
            "statusCode": 500,
            "body": "fail"
        }

    finally:
        if driver:
            try:
                chrome_driver.quit()
            except Exception as e:
                print(f"드라이버 정리 중 에러: {str(e)}")


if __name__ == "__main__":
    print("\n") # 그냥 빈줄용
    handler({}, None)
    