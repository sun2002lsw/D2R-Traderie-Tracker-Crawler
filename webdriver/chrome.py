from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .base import BaseDriver

class ChromeDriver(BaseDriver):
    def __init__(self):
        super().__init__()
        self._build_driver()

    def _build_driver(self):
        options = self._getChromeOptions()
        driver_path, chrome_path = self._validateEnvironment()
        
        options.binary_location = chrome_path
        self.driver = webdriver.Chrome(
            options=options, 
            executable_path=driver_path
        )
        self.driver.set_page_load_timeout(60)

    def _createChromeOptions(self):
        return Options()
