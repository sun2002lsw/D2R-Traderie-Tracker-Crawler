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

        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-setuid-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-software-rasterizer")
        opts.add_argument("--disable-features=VizDisplayCompositor")
        opts.add_argument("--disable-background-timer-throttling")
        opts.add_argument("--disable-backgrounding-occluded-windows")
        opts.add_argument("--disable-renderer-backgrounding")
        opts.add_argument("--disable-background-networking")
        opts.add_argument("--disable-field-trial-config")
        opts.add_argument("--disable-ipc-flooding-protection")
        opts.add_argument("--disable-hang-monitor")
        opts.add_argument("--disable-prompt-on-repost")
        opts.add_argument("--disable-client-side-phishing-detection")
        opts.add_argument("--disable-logging")
        opts.add_argument("--disable-logging-redirect")
        opts.add_argument("--no-zygote")
        opts.add_argument("--single-process")
        opts.add_argument("--process-per-site")
        opts.add_argument("--memory-pressure-off")
        opts.add_argument("--max_old_space_size=4096")
        opts.add_argument("--hide-scrollbars")
        opts.add_argument("--mute-audio")
        opts.add_argument("--window-size=1280,720")
        opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        opts.add_argument("--metrics-recording-only")
        opts.add_argument("--no-first-run")
        opts.add_argument("--no-default-browser-check")
        opts.add_argument("--aggressive-cache-discard")
        opts.add_argument("--disable-web-security")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-plugins")
        opts.add_argument("--disable-images")
        opts.add_argument("--disable-javascript")
        opts.add_argument("--disable-safebrowsing")
        opts.add_argument("--disable-component-update")
        opts.add_argument("--disable-default-apps")
        opts.add_argument("--disable-sync")
        opts.add_argument("--disable-translate")
        
        # 자동화 감지 방지
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        
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
