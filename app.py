from time import sleep
from webdriver import ChromeDriver
from crawler import Crawler
from db import DynamoDB
from datetime import datetime
import os


def handler(event, context):
    driver = None
    try:
        if not os.getenv('LOCAL_DEV'):
            print("DynamoDB 연결 테스트 시작...")
            db = DynamoDB()
            db.test_connection()
            print("DynamoDB 연결 테스트 완료")
        
        print("웹 드라이버 생성 시작...")
        chrome_driver = ChromeDriver()
        driver = chrome_driver.get_driver()
        print("웹 드라이버 생성 완료")

        print("웹 드라이버 접속 검증 시작...")
        driver.get("https://traderie.com/diablo2resurrected")
        sleep(10)
        if "error" in driver.current_url:
            print("웹 드라이버 접속 검증 실패")
            return {
                "statusCode": 500,
                "body": "fail"
            }
        print("웹 드라이버 접속 검증 완료")
        
        print("크롤러 생성 및 실행 시작...")
        crawler = Crawler(driver)
        result = crawler.run()
        print("크롤링 완료")
        
        if not os.getenv('LOCAL_DEV'):
            print("테스트 데이터 삽입 시작...")
            current_time = datetime.now().strftime("%m-%d %H:%M")
            test_items = {
                'item1': {'ItemName': 'test-001', 'registered_time': current_time, 'message': 'test item 1'},
                'item2': {'ItemName': 'test-002', 'registered_time': current_time, 'message': 'test item 2'},
                'item3': {'ItemName': 'test-003', 'registered_time': current_time, 'message': 'test item 3'}
            }
            db.put_items(test_items)
            print("테스트 데이터 삽입 완료")
        
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
    handler({}, None)
    