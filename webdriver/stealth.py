import os, re, json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class StealthDriver:
    """
    - 헤드리스 스텔스(지표 스푸핑 강화: UA/UA-CH/screen/permissions/hwc/mem/touch/WebGL/Canvas 등)
    - 초기엔 ServiceWorker 건드리지 않음(탐지 신호 최소화). 필요 시 외부에서 정지.
    - performance 로그 활성화(Validator가 Network.* 수집).
    - __init__ / _build_driver : 인자 없음.
    """
    def __init__(self):
        self.driver = None
        self._build_driver()

    def _build_driver(self):
        opts = Options()
        # Headless & Lambda
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,720")
        opts.add_argument("--lang=ko-KR")

        # 자동화 흔적 최소화
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument("--disable-blink-features=AutomationControlled")

        # 개인정보 샌드박스/광고 API만 비활성화(과도한 차단은 지양)
        opts.add_argument("--disable-features=InterestCohort,PrivacySandboxAdsAPIs,AttributionReporting")

        # (선택) 프록시: 환경변수 PROXY/HTTPS_PROXY/HTTP_PROXY 중 하나를 쓰고 싶으면 세팅
        proxy = os.environ.get("PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
        if proxy:
            opts.add_argument(f"--proxy-server={proxy}")

        # CDP 로그
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})

        # Lambda 바이너리 경로
        chrome_bin = os.environ.get("CHROME_BIN")
        chromedriver = os.environ.get("CHROMEDRIVER")
        if chrome_bin and os.path.exists(chrome_bin):
            opts.binary_location = chrome_bin

        if chromedriver:
            service = Service(executable_path=chromedriver)
            d = webdriver.Chrome(service=service, options=opts)
        else:
            d = webdriver.Chrome(options=opts)

        # 타임아웃
        d.set_page_load_timeout(30)
        d.implicitly_wait(8)

        # ── 스텔스 패치(JS) : webdriver/permissions/hwc/touch/plugins/connection/WebGL/Canvas 등
        stealth_js = r"""
        (function(){
          const navProto = Object.getPrototypeOf(navigator);

          // webdriver 숨김
          try{ Object.defineProperty(navProto,'webdriver',{get:()=>undefined}); }catch(e){}

          // 언어/플랫폼
          try{ Object.defineProperty(navProto,'languages',{get:()=>['ko-KR','ko','en-US','en']}); }catch(e){}
          try{ Object.defineProperty(navProto,'language',{get:()=> 'ko-KR'}); }catch(e){}
          try{ Object.defineProperty(navProto,'platform',{get:()=> 'Win32'}); }catch(e){}

          // 하드웨어/메모리/터치
          try{ Object.defineProperty(navProto,'hardwareConcurrency',{get:()=> 8}); }catch(e){}
          try{ Object.defineProperty(navProto,'deviceMemory',{get:()=> 8}); }catch(e){}
          try{ Object.defineProperty(navigator,'maxTouchPoints',{get:()=> 0}); }catch(e){}

          // chrome 객체/메서드 느낌 살리기
          if (!window.chrome) { try{ window.chrome = { runtime: {} }; }catch(e){} }
          try{
            // chrome.runtime 존재감 + 네이티브풍 toString
            Object.defineProperty(window.chrome, 'runtime', {value:{}});
            (window.chrome.runtime.toString = function(){ return 'function runtime() { [native code] }'; });
          }catch(e){}

          // plugins/mimeTypes 길이만 맞춤
          try{
            const _plugins = { length: 3, 0:{}, 1:{}, 2:{} };
            const _mimes   = { length: 3, 0:{}, 1:{}, 2:{} };
            Object.defineProperty(navProto,'plugins',{get:()=>_plugins});
            Object.defineProperty(navProto,'mimeTypes',{get:()=>_mimes});
          }catch(e){}

          // Permissions API: notifications 등 쿼리 결과 자연스럽게
          try{
            const _query = navigator.permissions && navigator.permissions.query;
            if (_query) {
              navigator.permissions.query = (p)=> {
                if (p && p.name === 'notifications') {
                  return Promise.resolve({ state: Notification.permission });
                }
                return _query.call(navigator.permissions, p);
              };
            }
          }catch(e){}

          // NetworkInformation 존재감(대략)
          try{
            if (!('connection' in navigator)) {
              Object.defineProperty(navigator,'connection',{ get:()=>({ effectiveType:'4g', rtt:50, downlink:10, saveData:false }) });
            }
          }catch(e){}

          // WebGL vendor/renderer
          try{
            const gp = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter=function(p){
              const V=0x9245,R=0x9246;
              if(p===V) return 'Google Inc.';
              if(p===R) return 'ANGLE (NVIDIA, NVIDIA GeForce, D3D11)';
              return gp.apply(this,[p]);
            };
          }catch(e){}

          // Canvas 미세 노이즈
          try{
            const t=HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL=function(){
              const c=this.getContext('2d'); if(c){c.globalAlpha=0.999; c.fillStyle='#000'; c.fillRect(0,0,1,1); c.globalAlpha=1;}
              return t.apply(this,arguments);
            };
          }catch(e){}
        })();
        """
        d.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": stealth_js})

        # ── CDP: Network/UA/Headers/Locale/TZ
        try:
            d.execute_cdp_cmd("Network.enable", {})
        except Exception:
            pass

        # UA 및 UA-CH 고정
        try:
            ua = d.execute_script("return navigator.userAgent") or ""
            m = re.search(r"Chrome/(\d+\.\d+\.\d+\.\d+)", ua)
            ver = m.group(1) if m else "120.0.0.0"
            major = ver.split(".",1)[0]
            ua2 = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36"
            ua2 = ua2.replace("HeadlessChrome", "Chrome")

            d.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": ua2,
                "platform": "Windows",
                "acceptLanguage": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "userAgentMetadata": {
                    "brands": [
                        {"brand":"Chromium","version":major},
                        {"brand":"Google Chrome","version":major},
                        {"brand":"Not A(Brand)","version":"99"}
                    ],
                    "fullVersion": ver,
                    "platform": "Windows",
                    "platformVersion": "10.0.0",
                    "architecture": "x86",
                    "model": "",
                    "mobile": False
                }
            })
            d.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {
                "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "sec-ch-ua": f"\"Chromium\";v=\"{major}\", \"Google Chrome\";v=\"{major}\", \"Not A;Brand\";v=\"99\"",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-ch-ua-mobile": "?0"
            }})
        except Exception as e:
            print(f"[CDP] UA/headers override 실패: {e}")

        # 화면 지표를 window-size와 일치시킴(Headless의 screen 800x600 흔적 해소)
        try:
            d.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 1280, "height": 720, "deviceScaleFactor": 1, "mobile": False
            })
        except Exception:
            pass

        # 로케일/타임존
        try:
            d.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": "ko-KR"})
        except Exception as e:
            print(f"[CDP] locale override 실패: {e}")
        try:
            d.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Asia/Seoul"})
        except Exception as e:
            print(f"[CDP] timezone override 실패: {e}")

        self.driver = d

    # 전역 Referer 부여(필요 시)
    def set_global_referer(self, referer: str):
        try:
            self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {
                "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "referer": referer
            }})
            print(f"[CDP] set referer={referer}")
        except Exception as e:
            print(f"[CDP] set referer 실패: {e}")

    # 전역 헤더 롤백
    def clear_extra_headers(self):
        try:
            self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {
                "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
            }})
            print("[CDP] cleared extra headers (kept accept-language)")
        except Exception as e:
            print(f"[CDP] clear headers 실패: {e}")

    # 모바일 프로필 스위치(필요 시)
    def switch_to_mobile_profile(self):
        d = self.driver
        try:
            d.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "platform": "Android",
                "acceptLanguage": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "userAgentMetadata": {
                    "brands": [
                        {"brand":"Chromium","version":"120"},
                        {"brand":"Google Chrome","version":"120"},
                        {"brand":"Not A(Brand)","version":"99"}
                    ],
                    "fullVersion": "120.0.0.0",
                    "platform": "Android",
                    "platformVersion": "13",
                    "architecture": "arm",
                    "model": "Pixel 7 Pro",
                    "mobile": True
                }
            })
            d.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "width": 390, "height": 844, "deviceScaleFactor": 3, "mobile": True
            })
            d.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {
                "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "sec-ch-ua": "\"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\", \"Not A;Brand\";v=\"99\"",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-ch-ua-mobile": "?1"
            }})
            print("[PROFILE] switched to Android mobile profile")
        except Exception as e:
            print(f"[PROFILE] mobile switch 실패: {e}")

    def get_driver(self):
        return self.driver

    def quit(self):
        try:
            self.driver.quit()
        except Exception:
            pass
