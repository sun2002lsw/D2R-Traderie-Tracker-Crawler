import undetected_chromedriver as uc
from .base import BaseDriver

class StealthDriver(BaseDriver):
    def __init__(self):
        super().__init__()
        self._build_driver()

    def _build_driver(self):
        options = self._getChromeOptions()
        driver_path, chrome_path = self._validateEnvironment()
            
        self.driver = uc.Chrome(
            options=options, 
            driver_executable_path=driver_path,
            browser_executable_path=chrome_path,
            headless=True
        )
        self.driver.set_page_load_timeout(60)

    def _createChromeOptions(self):
        return uc.ChromeOptions()
