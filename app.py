import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def build_driver():
    opts = Options()

    # Lambda 환경에 최적화된 Chrome 옵션
    opts.add_argument("--headless=new")  # 헤드리스 모드
    opts.add_argument("--no-sandbox")  # 샌드박스 비활성화
    opts.add_argument("--disable-dev-shm-usage")  # 공유메모리 비활성화
    opts.add_argument("--disable-gpu")  # GPU 비활성화
    opts.add_argument("--disable-web-security")  # 웹보안 비활성화
    opts.add_argument("--disable-extensions")  # 확장프로그램 비활성화
    opts.add_argument("--disable-plugins")  # 플러그인 비활성화
    opts.add_argument("--disable-images")  # 이미지 비활성화
    opts.add_argument("--disable-javascript")  # 자바스크립트 비활성화
    opts.add_argument("--disable-background-timer-throttling")  # 백그라운드 타이머 제한 해제
    opts.add_argument("--disable-backgrounding-occluded-windows")  # 백그라운드 윈도우 비활성화
    opts.add_argument("--disable-renderer-backgrounding")  # 렌더러 백그라운드 비활성화
    opts.add_argument("--disable-field-trial-config")  # 필드트라이얼 비활성화
    opts.add_argument("--disable-ipc-flooding-protection")  # IPC 플러딩 보호 해제
    opts.add_argument("--disable-hang-monitor")  # 행 모니터 비활성화
    opts.add_argument("--disable-prompt-on-repost")  # 재전송 프롬프트 비활성화
    opts.add_argument("--disable-client-side-phishing-detection")  # 클라이언트 피싱감지 비활성화
    opts.add_argument("--disable-component-update")  # 컴포넌트 업데이트 비활성화
    opts.add_argument("--disable-default-apps")  # 기본앱 비활성화
    opts.add_argument("--disable-sync")  # 동기화 비활성화
    opts.add_argument("--disable-translate")  # 번역 비활성화
    opts.add_argument("--metrics-recording-only")  # 메트릭만 기록
    opts.add_argument("--no-first-run")  # 첫실행 건너뛰기
    opts.add_argument("--safebrowsing-disable-auto-update")  # 안전브라우징 자동업데이트 비활성화
    opts.add_argument("--disable-safebrowsing")  # 안전브라우징 비활성화
    opts.add_argument("--disable-logging")  # 로깅 비활성화
    opts.add_argument("--disable-logging-redirect")  # 로깅 리다이렉트 비활성화
    opts.add_argument("--disable-background-networking")  # 백그라운드 네트워킹 비활성화
    opts.add_argument("--hide-scrollbars")  # 스크롤바 숨기기
    opts.add_argument("--mute-audio")  # 오디오 음소거
    opts.add_argument("--no-zygote")  # 자이고트 비활성화
    opts.add_argument("--single-process")  # 단일 프로세스
    opts.add_argument("--process-per-site")  # 사이트별 프로세스
    opts.add_argument("--aggressive-cache-discard")  # 적극적 캐시 삭제
    opts.add_argument("--memory-pressure-off")  # 메모리 압박 해제
    opts.add_argument("--max_old_space_size=4096")  # 최대 메모리 크기
    opts.add_argument("--window-size=1280,720")  # 윈도우 크기 설정
    opts.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")  # 사용자 에이전트 설정
    
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
