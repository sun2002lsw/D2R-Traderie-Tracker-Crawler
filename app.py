from webdriver import ChromeDriver
from crawler import Crawler


def handler(event, context):
    driver = None
    try:
        print("Chrome 드라이버 생성 시작...")
        chrome_driver = ChromeDriver()
        driver = chrome_driver.get_driver()
        print("Chrome 드라이버 생성 완료")
        
        print("크롤러 생성 및 실행 시작...")
        crawler = Crawler(driver)
        result = crawler.run()
        print("크롤링 완료")
        
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
    