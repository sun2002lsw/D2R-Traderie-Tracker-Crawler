import os
import undetected_chromedriver as uc
from .base import BaseDriver

class StealthDriver(BaseDriver):
    def __init__(self):
        super().__init__()
        self._build_driver()

    def _build_driver(self):
        if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
            os.environ['WDM_LOG_LEVEL'] = '0'
            os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
            os.environ['PYTHONPATH'] = '/var/task'
            os.environ['CHROME_BIN'] = '/opt/chrome/chrome'
            os.environ['CHROMEDRIVER'] = '/opt/chromedriver/chromedriver'
            
        options = self._getChromeOptions()
        driver_path, chrome_path = self._validateEnvironment()
            
        self.driver = uc.Chrome(
            options=options, 
            driver_executable_path=driver_path,
            browser_executable_path=chrome_path,
            version_main=None,
            use_subprocess=False,
            headless=True,
            suppress_welcome=True
        )
        self.driver.set_page_load_timeout(60)

    def _createChromeOptions(self):
        return uc.ChromeOptions()
