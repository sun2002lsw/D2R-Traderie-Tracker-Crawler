import time


class Crawler:
    def __init__(self, driver):
        self.driver = driver
    
    def run(self):
        self.driver.get("https://example.com")
        
        # 페이지 로딩 대기
        time.sleep(2)
        
        title = self.driver.title
        
        return {
            "statusCode": 200,
            "body": "success"
        }
