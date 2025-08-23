import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Crawler:
    def __init__(self, driver):
        self.driver = driver
    
    def login(self, traderie_id, traderie_pwd):
        self.driver.get("https://traderie.com/login")
        
        # input 요소가 나타날 때까지 대기 (10초 timeout)
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
        )
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        
        username_input.send_keys(traderie_id)
        password_input.send_keys(traderie_pwd)
        password_input.send_keys(Keys.RETURN)
        
        # 로그인 후 페이지 로딩 대기
        time.sleep(5)
    
    def run(self):
        traderie_id = os.environ.get('TRADERIE_ID')
        traderie_pwd = os.environ.get('TRADERIE_PWD')

        print("로그인 시도 중...")
        self.login(traderie_id, traderie_pwd)
        print("로그인 성공")
        
        return {
            "statusCode": 200,
            "body": "success"
        }
