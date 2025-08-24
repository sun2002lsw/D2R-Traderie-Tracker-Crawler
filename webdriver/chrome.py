import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class ChromeDriver:
    def __init__(self):
        self.driver = None
        self._build_driver()
    
    def _build_driver(self):
        opts = Options()

        # Headless 모드 (Lambda 환경 필수)
        opts.add_argument("--headless=new")
        
        # AWS Lambda 환경 필수 설정
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        
        # 윈도우 크기
        opts.add_argument("--window-size=1280,720")
        
        # 사용자 에이전트 (봇 감지 방지)
        opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        chrome_bin = os.environ.get("CHROME_BIN")
        chromedriver_path = os.environ.get("CHROMEDRIVER")
        
        if chrome_bin and os.path.exists(chrome_bin):
            opts.binary_location = chrome_bin
        
        if chromedriver_path:
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=opts)
        else:
            self.driver = webdriver.Chrome(options=opts)
        
        # 페이지 로드 타임아웃 설정
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
    
    def get_driver(self):
        return self.driver
    
    def quit(self):
        self.driver.quit()
