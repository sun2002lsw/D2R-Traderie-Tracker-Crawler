import os

class BaseDriver:
    def __init__(self):
        self.driver = None

    def _getChromeOptions(self):
        chrome_options = self._createChromeOptions()

        # 기본 보안 및 성능 옵션
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        
        # Dev Container 환경을 위한 추가 옵션
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-client-side-phishing-detection')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--safebrowsing-disable-auto-update')
        chrome_options.add_argument('--disable-hang-monitor')
        chrome_options.add_argument('--disable-prompt-on-repost')
        chrome_options.add_argument('--disable-domain-reliability')
        chrome_options.add_argument('--disable-component-update')
        chrome_options.add_argument('--disable-features=InterestBasedContentTargeting')
        
        # 메모리 및 성능 최적화
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--max_old_space_size=4096')
        
        # 사용자 에이전트 설정
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        return chrome_options

    def _createChromeOptions(self):
        raise NotImplementedError("하위 클래스에서 구현해야 합니다.")

    def _validateEnvironment(self):
        driver_path = os.environ.get("CHROMEDRIVER")
        chrome_path = os.environ.get("CHROME_BIN")
        if not driver_path:
            raise Exception("CHROMEDRIVER 환경 변수가 설정되지 않았습니다.")
        if not chrome_path:
            raise Exception("CHROME_BIN 환경 변수가 설정되지 않았습니다.")
            
        return driver_path, chrome_path

    def get_driver(self):
        return self.driver

    def quit(self):
        try:
            self.driver.quit()
        except Exception:
            pass
