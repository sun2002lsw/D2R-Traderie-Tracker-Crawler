# -*- coding: utf-8 -*-
import os
import json
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Crawler:
    def __init__(self, driver):
        # StealthDriver.get_driver()로 받은 WebDriver 인스턴스
        # (여기엔 d.GetUrl 이 바인딩되어 있어야 함)
        self.driver = driver

    # ─────────────────────────────────────────────────────────────
    # 네트워크 후킹: fetch/xhr -> window.__netlog
    # ─────────────────────────────────────────────────────────────
    def _install_net_probe(self):
        js = r"""
        (function(){
          if (window.__netlogInstalled) return;
          window.__netlogInstalled = true;
          window.__netlog = [];

          function push(e){
            try{
              window.__netlog.push(e);
              if (window.__netlog.length > 800) window.__netlog.shift();
            }catch(_){}
          }

          // fetch hook
          try{
            const _fetch = window.fetch;
            window.fetch = async function(input, init){
              const url = typeof input==='string' ? input : (input && input.url) || '';
              const method = (init && init.method) || 'GET';
              const t0 = Date.now();
              try{
                const resp = await _fetch.apply(this, arguments);
                push({type:'fetch', url, method, status: resp.status, dur: Date.now()-t0, t: Date.now()});
                return resp;
              }catch(e){
                push({type:'fetch', url, method, error: String(e), dur: Date.now()-t0, t: Date.now()});
                throw e;
              }
            };
          }catch(_){}

          // XHR hook
          try{
            const XHR = window.XMLHttpRequest;
            const open = XHR.prototype.open;
            const send = XHR.prototype.send;
            XHR.prototype.open = function(m,u){
              this.__m = m; this.__u = u;
              return open.apply(this, arguments);
            };
            XHR.prototype.send = function(b){
              const t0 = Date.now();
              this.addEventListener('loadend', ()=>{
                push({type:'xhr', url:this.__u||'', method:this.__m||'', status:this.status, dur: Date.now()-t0, t: Date.now()});
              });
              return send.apply(this, arguments);
            };
          }catch(_){}
        })();
        """
        try:
            self.driver.execute_script(js)
            print("[NET] probe installed")
        except Exception as e:
            print(f"[NET] probe install failed: {e}")

    def _read_netlog(self):
        try:
            return self.driver.execute_script("return window.__netlog ? window.__netlog.slice(-120) : [];")
        except Exception:
            return []

    def _dump_debug(self, tag="DEBUG"):
        d = self.driver
        try:
            names = [c.get("name") for c in d.get_cookies()]
        except Exception:
            names = []
        print(f"[{tag}] current_url={d.current_url}")
        print(f"[{tag}] cookies={names}")

        try:
            logs = d.get_log("browser")[-20:]
            if logs:
                print(f"[{tag}] console_tail({len(logs)})")
                for e in logs:
                    lvl = e.get("level"); msg = e.get("message", "")[:1000]
                    print(f" - [{lvl}] {msg}")
        except Exception:
            pass

        net = self._read_netlog()
        if net:
            print(f"[{tag}] net_tail({len(net)}) ->")
            for e in net[-30:]:
                t = e.get("type"); m = e.get("method"); st = e.get("status")
                u = (e.get("url") or "")[:160]
                err = e.get("error")
                if err:
                    print(f"  {t} {m} {u} ERR={err}")
                else:
                    print(f"  {t} {m} {u} ST={st}")

    def _last_same_origin_post(self):
        net = self._read_netlog()
        for e in reversed(net):
            if (e.get("method") or "").upper() == "POST":
                u = (e.get("url") or "")
                if "traderie.com" in u or u.startswith("/"):
                    return u, e.get("status"), e.get("error")
        return None, None, None

    def _has_cookie(self, name):
        try:
            return any((c.get("name")==name) for c in self.driver.get_cookies())
        except Exception:
            return False

    # ─────────────────────────────────────────────────────────────
    # CF/로그인 폼 감지 유틸
    # ─────────────────────────────────────────────────────────────
    def _wait_login_form_or_cf(self, timeout=20):
        """username 입력 또는 CF 챌린지(혹은 토큰 필드) 중 하나가 뜰 때까지 대기"""
        d = self.driver
        end = time.time() + timeout
        while time.time() < end:
            try:
                if d.find_elements(By.CSS_SELECTOR, 'input[name="username"]'):
                    return "form"
            except Exception:
                pass
            try:
                # turnstile iframe/hidden input 또는 cf-please-wait 패턴
                cf = d.execute_script("""
                  return !!(document.querySelector('iframe[src*="turnstile"],input[name="cf-turnstile-response"],#cf-please-wait,.cf-challenge'));
                """)
                if cf:
                    return "cf"
            except Exception:
                pass
            time.sleep(0.25)
        return None

    def _open_login_hard(self):
        """항상 하드 내비로 /login 오픈 (referer + SW kill)"""
        d = self.driver
        d.GetUrl("https://traderie.com/diablo2resurrected")
        WebDriverWait(d, 30).until(
            lambda x: x.execute_script("return document.readyState") in ("interactive", "complete")
        )
        d.GetUrl(
            "https://traderie.com/login",
            referer="https://traderie.com/diablo2resurrected",
            kill_sw=True
        )
        WebDriverWait(d, 30).until(
            lambda x: x.execute_script("return document.readyState") in ("interactive", "complete")
        )
        print("트레더리 로그인 페이지(하드 내비) 진입")

    # ─────────────────────────────────────────────────────────────
    # PUBLIC
    # ─────────────────────────────────────────────────────────────
    def run(self):
        traderie_id = os.environ.get('TRADERIE_ID')
        traderie_pwd = os.environ.get('TRADERIE_PWD')
        print(f"ID: {traderie_id}")
        print(f"PWD: {traderie_pwd}")

        print("로그인 시도 중...")
        self._login(traderie_id, traderie_pwd)
        print("로그인 성공")

        trade_lists = dict()
        for item_name, item_data in self._load_items().items():
            if item_data['id'] != -1:
                print(f"{item_name} 거래 기록 크롤링 시작")
                try:
                    trade_list = self._crawl_trade_list(item_data['id'])
                    trade_lists[item_name] = trade_list
                    print(f"{item_name} 거래 기록 크롤링 완료")
                except Exception as e:
                    print(f"{item_name} 거래 기록 크롤링 중 오류 발생: {e}")
        
        return trade_lists

    def _login(self, traderie_id, traderie_pwd):
        d = self.driver

        # 1) 로그인 페이지를 '하드 내비게이션'으로 오픈 (referer + SW kill)
        self._open_login_hard()

        # 2) 네트워크 후킹 주입
        self._install_net_probe()

        # 3) 로그인 폼 또는 CF 화면 대기
        state = self._wait_login_form_or_cf(timeout=20)
        print(f"[LOGIN] initial state = {state}")
        if state == "cf":
            # cf_clearance 쿠키를 잠깐 기다렸다가(있으면 리로드)
            t0 = time.time()
            while time.time() - t0 < 10 and not self._has_cookie("cf_clearance"):
                time.sleep(0.5)
            # cf_clearance가 생겼거나 시간이 지나도 폼이 안 보이면 1회 새로 열기
            self._open_login_hard()
            state = self._wait_login_form_or_cf(timeout=15)
            print(f"[LOGIN] after reopen state = {state}")

        if state != "form":
            self._dump_debug("LOGIN-PRE-FORM-FAIL")
            raise TimeoutException("로그인 폼을 찾지 못했습니다.")

        # 4) 폼 입력
        username_input = WebDriverWait(d, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
        )
        password_input = WebDriverWait(d, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
        )
        username_input.clear(); username_input.send_keys(traderie_id)
        password_input.clear(); password_input.send_keys(traderie_pwd)
        print("로그인 정보 작성")

        # 5) 제출
        try:
            submit = d.find_element(By.CSS_SELECTOR, 'form button[type="submit"], button[type="submit"]')
            d.execute_script("arguments[0].click();", submit)
            print("로그인 전송 버튼 클릭")
        except Exception:
            password_input.send_keys(Keys.RETURN)
            print("로그인 전송 엔터 누름")

        # 6) URL 전이 또는 same-origin POST 대기
        ok = self._wait_login_transition_or_post(timeout=25)
        post_url, post_st, post_err = self._last_same_origin_post()
        print(f"[LOGIN] last POST -> url={post_url} status={post_st} err={post_err}")

        # 7) 실패(403 등)면 1회 재시도: /login 다시 열고 다시 제출
        if not ok or (post_st and str(post_st) == "403"):
            print("[LOGIN] 1st attempt looks blocked → retry once")
            self._open_login_hard()
            self._install_net_probe()
            WebDriverWait(d, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]')))
            d.find_element(By.CSS_SELECTOR, 'input[name="username"]').send_keys(traderie_id)
            d.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(traderie_pwd)
            try:
                d.find_element(By.CSS_SELECTOR, 'form button[type="submit"], button[type="submit"]').click()
            except Exception:
                d.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(Keys.RETURN)

            ok = self._wait_login_transition_or_post(timeout=25)
            post_url, post_st, post_err = self._last_same_origin_post()
            print(f"[LOGIN-RETRY] last POST -> url={post_url} status={post_st} err={post_err}")

        # 8) 로그인 성공/실패 최종 판정
        if ok:
            try:
                WebDriverWait(d, 8).until(lambda drv: "login" not in drv.current_url)
            except TimeoutException:
                # URL 그대로여도 인증된 UI가 있으면 OK로 본다
                try:
                    WebDriverWait(d, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/logout'], a[href='/account'], [data-testid='user-menu']"))
                    )
                    print("[LOGIN] 인증된 UI 감지됨(로그아웃/계정 메뉴).")
                    return
                except TimeoutException:
                    pass

        # 여기 도달하면 실패
        self._dump_debug("LOGIN-FINAL-FAIL")
        raise TimeoutException("로그인 완료 전환 실패(페이지가 /login에 머무름).")

    def _wait_login_transition_or_post(self, timeout=20):
        d = self.driver
        end = time.time() + timeout
        while time.time() < end:
            try:
                if "login" not in d.current_url:
                    return True
            except Exception:
                pass
            try:
                net = self._read_netlog()
                for e in reversed(net):
                    if (e.get("method") or "").upper() == "POST":
                        u = (e.get("url") or "")
                        if "traderie.com" in u or u.startswith("/"):
                            return True
            except Exception:
                pass
            time.sleep(0.25)
        return False

    def _load_items(self):
        json_path = os.path.join(os.path.dirname(__file__), 'traderie_items.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _crawl_trade_list(self, item_id):
        url = f"https://traderie.com/diablo2resurrected/product/{item_id}/recent?prop_Mode=softcore&prop_Ladder=true"
        self.driver.GetUrl(url)
        offer_table = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.offer-table'))
        )
        for trade_div in offer_table.find_elements(By.CSS_SELECTOR, 'div'):
            self._refine_trade(trade_div)
    
    def _refine_trade(self, trade_div):
        print(trade_div.text.strip())
