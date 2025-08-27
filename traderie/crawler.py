import os
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Crawler:
    def __init__(self, web_driver):
        self.web_driver = web_driver

    def run(self):
        traderie_id = os.environ["TRADERIE_ID"]
        traderie_pwd = os.environ["TRADERIE_PWD"]
        print(f"TRADERIE_ID: {traderie_id}")
        print(f"TRADERIE_PWD: {traderie_pwd}")

        print(f"로그인 시작")
        self._login(traderie_id, traderie_pwd)
        print(f"로그인 완료\n")

        trade_lists = dict()
        for item_name in self._load_items():
            print(f"{item_name} 거래 기록 크롤링 시작")
            try:
                item_id = self._get_traderie_item_id(item_name)
                print(f"{item_name} => {item_id}")
                trade_lists[item_name] = self._crawl_trade_list(item_id)
                print(f"{item_name} 거래 기록 크롤링 완료\n")
            except Exception as e:
                print(f"{item_name} 거래 기록 크롤링 중 오류 발생: {e}\n")
    
    def _login(self, traderie_id, traderie_pwd):
        url = f"https://traderie.com/login"
        self.web_driver.get(url)

        # 페이지가 로딩 되기를 기다림
        username_input = WebDriverWait(self.web_driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
        )
        password_input = WebDriverWait(self.web_driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        print(f"로그인 페이지 로딩 완료")

        # 로그인
        username_input.send_keys(traderie_id)
        password_input.send_keys(traderie_pwd)
        password_input.send_keys(Keys.ENTER)

        # 로그인 되기를 대기
        WebDriverWait(self.web_driver, 30).until(lambda driver: "login" not in driver.current_url)

    def _load_items(self):
        json_path = os.path.join(os.path.dirname(__file__), 'traderie_items.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_traderie_item_id(self, item_name):
        item_name = item_name.replace(" ", "%20")
        url = f"https://traderie.com/diablo2resurrected/products?search={item_name}"
        self.web_driver.get(url)

        search_content_div = WebDriverWait(self.web_driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-content"))
        )
        fade_div = WebDriverWait(search_content_div, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.fade"))
        )
        row_div = WebDriverWait(fade_div, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.row"))
        )
        col_divs = WebDriverWait(row_div, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='col']"))
        )
        item_divs = WebDriverWait(col_divs, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.item"))
        )
        item_img1 = WebDriverWait(item_divs, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='item']"))
        )
        item_img2 = WebDriverWait(item_img1, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.item-container-img-icon"))
        )
        item_a_tag = WebDriverWait(item_img2, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='item-img']"))
        )

        # href 속성 꺼내오기
        href = item_a_tag.get_attribute("href")
        print(f"href: {href}")
        
        item_id = href.split("/")[-1]
        return item_id

    def _crawl_trade_list(self, item_id):
        url = f"https://traderie.com/diablo2resurrected/product/{item_id}/recent?prop_Mode=softcore&prop_Ladder=true"
        self.web_driver.get(url)

        # offer-table이 로딩되기를 기다림
        offer_table = WebDriverWait(self.web_driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.offer-table'))
        )
        print(f"거래 테이블 로딩 완료")

        # listing-product-info 요소들이 로딩되기를 기다림 (20개 또는 최대 30초)
        def wait_for_listings_loaded(driver):
            listings = driver.find_elements(By.CSS_SELECTOR, 'div.listing-product-info')
            return len(listings) >= 20

        WebDriverWait(self.web_driver, 30).until(wait_for_listings_loaded)
        
        # 로딩된 거래 개수 확인
        listings = self.web_driver.find_elements(By.CSS_SELECTOR, 'div.listing-product-info')
        print(f"{len(listings)}개의 거래 로딩 완료")

        for listing in listings:
            self._refine_trade(listing)
    
    def _refine_trade(self, listing):
        print(listing.text.strip())
