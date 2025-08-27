import os
import webdriver
import traderie
from db import DynamoDB
from datetime import datetime


def handler(event, context):
    driver = None

    try:
        if not os.getenv('LOCAL_DEV'):
            print("===== DynamoDB 연결 테스트 시작 =====")
            db = DynamoDB()
            db.test_connection()
            print("===== DynamoDB 연결 테스트 완료 =====\n")
        
        print("===== 웹 드라이버 생성 시작... =====")
        chrome_driver = webdriver.StealthDriver()
        driver = chrome_driver.get_driver()
        print("===== 웹 드라이버 생성 완료 =====\n")

        print("===== 크롤링 시작 =====")
        crawler = traderie.Crawler(driver)
        result = crawler.run()
        print("===== 크롤링 완료 =====\n")
        
        if not os.getenv('LOCAL_DEV'):
            print("===== 테스트 데이터 삽입 시작 =====")
            current_time = datetime.now().strftime("%m-%d %H:%M")
            test_items = {
                'item1': {'ItemName': 'test-001', 'registered_time': current_time, 'message': 'test item 1'},
                'item2': {'ItemName': 'test-002', 'registered_time': current_time, 'message': 'test item 2'},
                'item3': {'ItemName': 'test-003', 'registered_time': current_time, 'message': 'test item 3'}
            }
            db.put_items(test_items)
            print("===== 테스트 데이터 삽입 완료 =====\n")
        
        return result
        
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
    