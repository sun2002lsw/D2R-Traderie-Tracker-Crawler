import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def build_driver():
    opts = Options()

    # Lambda 환경에 최적화된 Chrome 옵션
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-images")
    opts.add_argument("--disable-javascript")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-field-trial-config")
    opts.add_argument("--disable-ipc-flooding-protection")
    opts.add_argument("--disable-hang-monitor")
    opts.add_argument("--disable-prompt-on-repost")
    opts.add_argument("--disable-client-side-phishing-detection")
    opts.add_argument("--disable-component-update")
    opts.add_argument("--disable-default-apps")
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-translate")
    opts.add_argument("--metrics-recording-only")
    opts.add_argument("--no-first-run")
    opts.add_argument("--safebrowsing-disable-auto-update")
    opts.add_argument("--disable-safebrowsing")
    opts.add_argument("--disable-logging")
    opts.add_argument("--disable-logging-redirect")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--mute-audio")
    opts.add_argument("--no-zygote")
    opts.add_argument("--single-process")
    opts.add_argument("--process-per-site")
    opts.add_argument("--aggressive-cache-discard")
    opts.add_argument("--memory-pressure-off")
    opts.add_argument("--max_old_space_size=4096")
    opts.add_argument("--window-size=1280,720")
    opts.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")
    
    # Lambda 환경 변수 확인
    chrome_bin = os.environ.get("CHROME_BIN", "/opt/chrome/chrome")
    chromedriver_path = os.environ.get("CHROMEDRIVER", "/opt/chromedriver/chromedriver")
    
    if os.path.exists(chrome_bin):
        opts.binary_location = chrome_bin
    
    # ChromeDriver 서비스 설정
    service = Service(executable_path=chromedriver_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=opts)
        # 페이지 로드 타임아웃 설정
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(f"Chrome 드라이버 생성 실패: {str(e)}")
        raise

def handler(event, context):
    driver = None
    try:
        print("Chrome 드라이버 생성 시작...")
        driver = build_driver()
        print("Chrome 드라이버 생성 완료")
        
        print("웹페이지 접속 시작...")
        driver.get("https://example.com")
        print("웹페이지 접속 완료")
        
        # 페이지 로딩 대기
        time.sleep(2)
        
        title = driver.title
        print(f"페이지 제목: {title}")
        
        return {
            "statusCode": 200,
            "body": {
                "success": True,
                "title": title,
                "message": "페이지 크롤링 성공"
            }
        }
        
    except Exception as e:
        error_msg = f"에러 발생: {str(e)}"
        print(error_msg)
        return {
            "statusCode": 500,
            "body": {
                "success": False,
                "error": error_msg,
                "type": type(e).__name__
            }
        }
    finally:
        if driver:
            try:
                driver.quit()
                print("Chrome 드라이버 정리 완료")
            except Exception as e:
                print(f"드라이버 정리 중 에러: {str(e)}")
