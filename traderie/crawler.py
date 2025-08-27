import time
import os
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Crawler:
    def __init__(self, driver):
        self.driver = driver

    def run(self):
        traderie_id = os.environ.get('TRADERIE_ID')
        traderie_pwd = os.environ.get('TRADERIE_PWD')
        print(f"ID: {traderie_id}")
        print(f"PWD: {traderie_pwd}")

        print("로그인 시도 중...")
        self._login(traderie_id, traderie_pwd)
        print("로그인 성공")

        trade_lists = dict()
        for item_name, item_data in self._load_items().items():
            if item_data['id'] != -1:
                print(f"{item_name} 거래 기록 크롤링 시작")
                try:
                    trade_list = self._crawl_trade_list(item_data['id'])
                    trade_lists[item_name] = trade_list
                    print(f"{item_name} 거래 기록 크롤링 완료")
                except Exception as e:
                    print(f"{item_name} 거래 기록 크롤링 중 오류 발생: {e}")
        
        return trade_lists

    def _login(self, traderie_id, traderie_pwd):
        self.driver.get("https://traderie.com/login")
        
        username_input = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
        )
        password_input = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        print("로그인 페이지 로딩 완료")
        
        username_input.send_keys(traderie_id)
        password_input.send_keys(traderie_pwd)
        password_input.send_keys(Keys.RETURN)
        print("로그인 정보 입력")
        
        WebDriverWait(self.driver, 30).until(
            lambda d: "login" not in d.current_url
        )
    
    def _load_items(self):
        json_path = os.path.join(os.path.dirname(__file__), 'traderie_items.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _crawl_trade_list(self, item_id):
        url = f"https://traderie.com/diablo2resurrected/product/{item_id}/recent?prop_Mode=softcore&prop_Ladder=true"
        self.driver.get(url)
        
        offer_table = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.offer-table'))
        )
        
        for trade_div in offer_table.find_elements(By.CSS_SELECTOR, 'div'):
            self._refine_trade(trade_div)
    
    def _refine_trade(self, trade_div):
        print(trade_div.text.strip())
