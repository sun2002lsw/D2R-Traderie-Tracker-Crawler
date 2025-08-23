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

        print("로그인 시도 중...")
        self._login(traderie_id, traderie_pwd)
        print("로그인 성공")

        print(self.driver.current_url)
        
        self.driver.get("https://traderie.com/")
        time.sleep(10)
        
        if "traderie.com/error" in self.driver.current_url:
            print("에러 페이지로 리다이렉트됨 - 차단 감지됨")
        else:
            print(self.driver.current_url)

        self.driver.get("https://traderie.com/diablo2resurrected")
        time.sleep(10)

        if "traderie.com/error" in self.driver.current_url:
            print("에러 페이지로 리다이렉트됨 - 차단 감지됨")
        else:
            print(self.driver.current_url)

        for item_name, item_data in self._load_items().items():
            if item_data['id'] != -1:
                print(f"{item_name} 거래 기록 크롤링 시작")
                try:
                    success = self._crawl_trade_list(item_data['id'])
                    if success:
                        print(f"{item_name} 거래 기록 크롤링 완료")
                        time.sleep(15)
                    else:
                        print(f"{item_name} 차단됨 - 60초 대기 후 다음 아이템으로")
                        time.sleep(60)
                except Exception as e:
                    print(f"{item_name} 거래 기록 크롤링 중 오류 발생: {e}")
                    time.sleep(30)
        
        return {
            "statusCode": 200,
            "body": "success"
        }

    def _login(self, traderie_id, traderie_pwd):
        self.driver.get("https://traderie.com/login")
        
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
        )
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        
        username_input.send_keys(traderie_id)
        password_input.send_keys(traderie_pwd)
        password_input.send_keys(Keys.RETURN)
        
        time.sleep(10)
    
    def _load_items(self):
        json_path = os.path.join(os.path.dirname(__file__), 'traderie_items.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _crawl_trade_list(self, item_id):
        url = f"https://traderie.com/diablo2resurrected/product/{item_id}?prop_Mode=softcore&prop_Ladder=true"
        
        try:
            self.driver.get(url)
            time.sleep(8)
            
            if "traderie.com/error" in self.driver.current_url:
                print("에러 페이지로 리다이렉트됨 - 차단 감지됨")
                return False
            
            offer_table = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.offer-table'))
            )
            
            for trade_div in offer_table.find_elements(By.CSS_SELECTOR, 'div'):
                self._refine_trade(trade_div)
            
            return True
                
        except Exception as e:
            print(f"offer-table을 찾을 수 없습니다: {e}")
            print("현재 페이지 제목:", self.driver.title)
            print("현재 URL:", self.driver.current_url)
            
            if "traderie.com/error" in self.driver.current_url:
                print("에러 페이지로 리다이렉트됨 - 차단 감지됨")
                return False
            
            page_source = self.driver.page_source
            print("페이지 소스 (처음 1000자):", page_source[:1000])
            
            all_divs = self.driver.find_elements(By.CSS_SELECTOR, 'div')
            print(f"페이지에 총 {len(all_divs)}개의 div가 있습니다.")
            
            for i, div in enumerate(all_divs[:5]):
                div_text = div.text.strip()
                if div_text:
                    print(f"div {i+1}: {div_text[:200]}...")
            
            return False
    
    def _refine_trade(self, trade_div):
        print(trade_div.text.strip())
