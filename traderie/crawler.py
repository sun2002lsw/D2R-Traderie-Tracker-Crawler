import os
from urllib.parse import quote

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Crawler:
    def __init__(self, web_driver):
        self.web_driver = web_driver

    def crawl_trade_list(self, item_name):
        traderie_id = os.environ["TRADERIE_ID"]
        traderie_pwd = os.environ["TRADERIE_PWD"]
        print(f"TRADERIE_ID: {traderie_id}")
        print(f"TRADERIE_PWD: {traderie_pwd}")

        print(f"로그인 시작")
        self._login(traderie_id, traderie_pwd)
        print(f"로그인 완료\n")

        print(f"{item_name} 아이템 크롤링 시작")
        item_id = self._get_traderie_item_id(item_name)
        print(f"{item_name} => {item_id}")
        trade_list = self._crawl_trade_list(item_id)
        print(f"{item_name} 아이템 크롤링 완료")

        return trade_list

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
        WebDriverWait(self.web_driver, 30).until(
            lambda driver: "login" not in driver.current_url
        )

    def _get_traderie_item_id(self, item_name):
        encoded_item_name = quote(item_name)
        url = (
            f"https://traderie.com/diablo2resurrected/products?"
            f"search={encoded_item_name}"
        )
        self.web_driver.get(url)

        item_a_tag = WebDriverWait(self.web_driver, 30).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.search-content div.fade div.row div[class*='col'] "
                    "div.item div[class*='item'] div.item-container-img-icon "
                    "a[class*='item-img']",
                )
            )
        )
        print(f"{item_name} 검색 페이지 로딩 완료")

        # href 속성 꺼내오기
        href = item_a_tag.get_attribute("href")
        return href.split("/")[-1]

    def _crawl_trade_list(self, item_id):
        url = (
            f"https://traderie.com/diablo2resurrected/product/"
            f"{item_id}/recent?"
            f"prop_Mode=softcore&prop_Ladder=true"
        )
        self.web_driver.get(url)

        # listing-product-info 요소들이 로딩되기를 기다림 (20개 또는 최대 30초)
        def wait_for_listings_loaded(driver):
            listings = driver.find_elements(By.CSS_SELECTOR, "div.listing-product-info")
            return len(listings) >= 20

        WebDriverWait(self.web_driver, 30).until(wait_for_listings_loaded)

        # 로딩된 거래 개수 확인
        listings = self.web_driver.find_elements(
            By.CSS_SELECTOR, "div.listing-product-info"
        )
        print(f"{len(listings)}개의 거래 확인됨")

        # 각각 거래 목록에 대해 파싱
        trade_list = list()
        for listing in listings:
            trade_info = self._refine_trade(listing)
            if trade_info:
                trade_list.append(trade_info)

        return trade_list

    def _refine_trade(self, listing):
        lines = listing.text.split("\n")
        if "day" in lines[-1]:
            return  # 24시간 이상 거래 제외

        start_index = lines.index("Trading For")
        end_index = next(i for i, line in enumerate(lines) if "High Rune Value" in line)
        trading_for_lines = lines[start_index + 1 : end_index]

        if any("each" in line for line in trading_for_lines):
            return  # each 거래는 뭔가 가치 판단이 어려워서 제외
        if any(
            ("Rune" not in line) and (" OR" not in line) for line in trading_for_lines
        ):
            return  # "Rune"도 아니고 " OR"도 아닌 항목이라면, 아이템이 끼어 있는 것

        trading_for_list = list()
        trading_for_items = list()
        for trading_for_line in trading_for_lines:
            if " OR" in trading_for_line:
                trading_for_list.append(trading_for_items)
                trading_for_items = list()
            else:
                trading_item = self._get_trading_item(trading_for_line)
                trading_for_items.append(trading_item)

        if trading_for_items:
            trading_for_list.append(trading_for_items)

        sell_amount = lines[0].split("X")[0].strip()  # "7 X Ist Rune" => 7
        print(f"{sell_amount}개의 물품을 판매: {trading_for_list}")
        return (sell_amount, trading_for_list)

    def _get_trading_item(self, trading_for_line):
        trade_info = trading_for_line.split("X")
        item_cnt = int(trade_info[0].strip())
        item_name = trade_info[1].strip()

        return (item_cnt, item_name)
