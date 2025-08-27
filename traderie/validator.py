import time
import json
from urllib.parse import urlparse

class BotDetectionError(Exception):
    """Raised when bot/anti-automation detection is suspected."""
    pass


class Validator:
    """
    Traderie 연결 진단기 (강화판).
    - Preload 훅 + 페이지 내 probe로 fetch/XHR/console/captcha/CF/에러/CSP/리소스 타이밍 로깅
    - 추가: CDP 'performance' 로그로 Network.* 이벤트 수집 (CSP/초기 네비까지 확실)
    - 1단계: /diablo2resurrected → 2단계: /login
    - 의심 시 복구 시도 후 BotDetectionError 발생
    """

    FIRST_URL  = "https://traderie.com/diablo2resurrected"
    SECOND_URL = "https://traderie.com/login"
    ORIGIN     = "https://traderie.com"
    FIRST_PARTY_HOST = "traderie.com"

    PROBE_JS = r"""
    (function(){
      if (window.__probe) return;
      window.__probe = { logs: [], net: [], captcha:false, marks: [] };

      // console 후킹
      ['log','info','warn','error'].forEach(function(k){
        const o = console[k];
        console[k] = function(){
          try{ window.__probe.logs.push({l:k,m:[].slice.call(arguments).join(' '),t:Date.now()}); }catch(e){}
          return o.apply(console, arguments);
        };
      });

      // page errors / unhandledrejection / CSP
      try{
        window.addEventListener('error', function(e){
          try{ window.__probe.logs.push({l:'pageerror', m:String(e.message||e.error||'error'), s:(e.filename+':'+e.lineno+':'+e.colno), t:Date.now()}); }catch(_){}
        });
        window.addEventListener('unhandledrejection', function(e){
          try{ window.__probe.logs.push({l:'promise', m:String(e.reason), t:Date.now()}); }catch(_){}
        });
        window.addEventListener('securitypolicyviolation', function(e){
          try{ window.__probe.logs.push({l:'csp', m:(e.violatedDirective||'')+' '+(e.blockedURI||''), t:Date.now()}); }catch(_){}
        });
      }catch(_){}

      // fetch/XHR 후킹
      (function(){
        const _fetch = window.fetch;
        window.fetch = async function(input, init){
          const url = typeof input==='string' ? input : (input && input.url) || '';
          const method = (init && init.method) || 'GET';
          const body = (init && init.body) ? String(init.body) : null;
          const t0 = Date.now();
          try{
            const resp = await _fetch.apply(this, arguments);
            try{ window.__probe.net.push({type:'fetch', url, method, bl: body?body.length:0, status: resp.status, dur: Date.now()-t0, t:Date.now()}); }catch(e){}
            return resp;
          }catch(e){
            try{ window.__probe.net.push({type:'fetch', url, method, bl: body?body.length:0, err: String(e), t:Date.now()}); }catch(_){}
            throw e;
          }
        };

        const _open = XMLHttpRequest.prototype.open;
        const _send = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.open = function(m,u){ this.__m=m; this.__u=u; return _open.apply(this,arguments); };
        XMLHttpRequest.prototype.send = function(b){
          const s=Date.now();
          this.addEventListener('loadend', ()=>{
            try{ window.__probe.net.push({type:'xhr', url:this.__u, method:this.__m, status:this.status, bl: b?String(b).length:0, dur:Date.now()-s, t:Date.now()}); }catch(e){}
          });
          return _send.apply(this, arguments);
        };
      })();

      // 캡차/Cloudflare 간단 감지
      function hasCaptcha(){
        try{
          if (document.querySelector('iframe[src*=\"hcaptcha\"],iframe[src*=\"recaptcha\"],iframe[src*=\"turnstile\"],#cf-please-wait,.cf-challenge,[data-sitekey]')) return true;
        }catch(e){}
        return false;
      }
      window.__probe.captcha = hasCaptcha();
      window.__probe.marks.push({k:'inject', t: Date.now(), href: location.href});
    })();
    """

    PRELOAD_JS = PROBE_JS  # 새 문서마다 가장 먼저 심음

    def __init__(self, driver):
        self.driver = driver
        self._preload_installed = False
        self._perf = {}  # requestId -> record

    # ── Public ───────────────────────────────────────────────────────
    def test_connection(self):
        d = self.driver
        self._divider("START")
        self._enable_cdp_network()
        self._arm_probe_on_new_document()

        # STEP1
        self._perf_start()
        print(f"[STEP1] open: {self.FIRST_URL}")
        d.get(self.FIRST_URL)
        self._inject_probe()
        self._fp_snapshot("STEP1")
        ok1, n1, t1 = self._dom_ready_hint()
        print(f"[STEP1] dom_ready={ok1} nodes≈{n1} text≈{t1}")
        cf1, cap1, net1, res1, stats1 = self._summary("STEP1")
        pstats1 = self._perf_summary("STEP1")  # ★ CDP 성능 로그 요약
        self._humanize()

        # STEP2
        self._perf_start()
        print(f"[STEP2] open: {self.SECOND_URL}")
        d.get(self.SECOND_URL)
        self._inject_probe()
        self._fp_snapshot("STEP2")
        ok2, n2, t2 = self._dom_ready_hint()
        print(f"[STEP2] dom_ready={ok2} nodes≈{n2} text≈{t2}")
        cf2, cap2, net2, res2, stats2 = self._summary("STEP2")
        pstats2 = self._perf_summary("STEP2")

        suspected, reasons = self._suspected_block(
            ok1=ok1, ok2=ok2, net1=net1, net2=net2, cf2=cf2, cap2=cap2,
            stats2=stats2, pstats2=pstats2
        )
        print(f"[RESULT] suspected_block={suspected} reasons={reasons}")

        if suspected:
            self._clear_origin()
            time.sleep(0.5)
            print(f"[RECOVER] retry: {self.SECOND_URL}")
            d.get(self.SECOND_URL)
            self._inject_probe()
            self._fp_snapshot("RECOVER")
            ok3, n3, t3 = self._dom_ready_hint()
            print(f"[RECOVER] dom_ready={ok3} nodes≈{n3} text≈{t3}")
            self._summary("RECOVER")
            self._perf_summary("RECOVER")
            self._divider("END")
            raise BotDetectionError(f"Bot/CF suspected: {', '.join(reasons)}")

        self._divider("END")

    # ── Private: UI/log helpers ──────────────────────────────────────
    def _divider(self, title: str):
        print("\n" + "="*30 + f" {title} " + "="*30)

    def _enable_cdp_network(self):
        try:
            self.driver.execute_cdp_cmd("Network.enable", {})
            print("[CDP] Network enabled")
        except Exception as e:
            print(f"[CDP] Network enable 실패: {e}")

    def _arm_probe_on_new_document(self):
        if self._preload_installed:
            return
        try:
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": self.PRELOAD_JS})
            self._preload_installed = True
            print("[PRELOAD] probe armed for new documents")
        except Exception as e:
            print(f"[PRELOAD] 실패: {e}")

    def _inject_probe(self):
        try:
            self.driver.execute_script(self.PROBE_JS)
            print("[INJECT] probe installed")
        except Exception as e:
            print(f"[INJECT] 실패: {e}")

    # ── Private: in-page probe read ──────────────────────────────────
    def _read_tail(self):
        try:
            data = self.driver.execute_script("""
              (function(){
                try{
                  var p = window.__probe;
                  var out = {logs:[], net:[], captcha:false, marks:[], res:[], mem:null};
                  if (p){
                    try{ out.logs = (p.logs||[]).slice(-50); }catch(e){}
                    try{ out.net  = (p.net||[]).slice(-50); }catch(e){}
                    try{ out.captcha = !!p.captcha; }catch(e){}
                    try{ out.marks = p.marks||[]; }catch(e){}
                  }
                  try{
                    var ents = (performance.getEntriesByType && performance.getEntriesByType('resource')) || [];
                    out.res = Array.prototype.slice.call(ents, -50).map(function(e){
                      return {
                        name: String(e.name||''),
                        it: String(e.initiatorType||''),
                        ts: Number(e.transferSize||0),
                        eb: Number(e.encodedBodySize||0),
                        proto: String(e.nextHopProtocol||'')
                      };
                    });
                  }catch(e){ out.res = []; }
                  try{
                    var mem = performance && performance.memory ? performance.memory : null;
                    out.mem = mem ? {
                      jsHeapSizeLimit: Number(mem.jsHeapSizeLimit||0),
                      totalJSHeapSize: Number(mem.totalJSHeapSize||0),
                      usedJSHeapSize: Number(mem.usedJSHeapSize||0)
                    } : null;
                  }catch(e){ out.mem = null; }
                  return out;
                }catch(e){
                  return {err:String(e)};
                }
              })();
            """)
            if not data or not isinstance(data, dict):
                print("[PROBE] empty read (likely very-early nav or CSP sandbox)")
                return [], [], False, [], None
            logs = list(data.get("logs") or [])[-50:]
            net  = list(data.get("net")  or [])[-50:]
            cap  = bool(data.get("captcha") or False)
            res  = list(data.get("res")  or [])[-50:]
            mem  = data.get("mem", None)
            return logs, net, cap, res, mem
        except Exception as e:
            print(f"[PROBE] read 실패: {e}")
            return [], [], False, [], None

    def _cookie_names(self):
        try:
            return [c.get("name") for c in self.driver.get_cookies()]
        except Exception:
            return []

    def _has_cf(self, names):
        s = set(n.lower() for n in names)
        return any(k in s for k in ("__cf_bm", "cf_clearance", "cf_chl_2", "cf_chl_prog"))

    def _dom_ready_hint(self, timeout=8):
        end = time.time() + timeout
        last_nodes, last_text = 0, 0
        while time.time() < end:
            try:
                nodes = self.driver.execute_script("return document.getElementsByTagName('*').length||0")
                textlen = self.driver.execute_script("return (document.body && document.body.innerText)?document.body.innerText.length:0")
                if nodes >= 80 and textlen >= 200:
                    return True, nodes, textlen
                last_nodes, last_text = nodes, textlen
            except Exception:
                pass
            time.sleep(0.25)
        return False, last_nodes, last_text

    def _fp_snapshot(self, tag: str):
        try:
            data = self.driver.execute_script("""
              try{
                return {
                  ua: navigator.userAgent,
                  wd: navigator.webdriver,
                  lang: navigator.language,
                  langs: navigator.languages,
                  tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
                  chromeObj: !!window.chrome,
                  uad: (navigator.userAgentData ? {brands: navigator.userAgentData.brands, mobile: navigator.userAgentData.mobile} : null),
                  scr: {w: screen.width, h: screen.height, aw: screen.availWidth, ah: screen.availHeight, dpr: window.devicePixelRatio, ow: window.outerWidth, oh: window.outerHeight},
                  rs: document.readyState,
                  vs: document.visibilityState,
                  ref: document.referrer
                };
              }catch(e){ return {err:String(e)}; }
            """)
            print(f"[{tag} FP] ua={data.get('ua')}")
            print(f"[{tag} FP] webdriver={data.get('wd')} lang={data.get('lang')} langs={data.get('langs')}")
            print(f"[{tag} FP] timezone={data.get('tz')} window.chrome={data.get('chromeObj')} uad={data.get('uad')}")
            scr = data.get('scr') or {}
            print(f"[{tag} FP] screen={{'w': {scr.get('w')}, 'h': {scr.get('h')}, 'aw': {scr.get('aw')}, 'ah': {scr.get('ah')}, 'dpr': {scr.get('dpr')}, 'ow': {scr.get('ow')}, 'oh': {scr.get('oh')}}} rs={data.get('rs')} vs={data.get('vs')} ref={data.get('ref')}")
        except Exception as e:
            print(f"[{tag} FP] snapshot 실패: {e}")

    # ── Private: perf(Network.*) 수집/요약 ────────────────────────────
    def _perf_start(self):
        self._perf = {}

    def _perf_ingest(self):
        logs = []
        try:
            logs = self.driver.get_log("performance")  # [{level, message, timestamp}]
        except Exception:
            return
        for entry in logs:
            try:
                msg = json.loads(entry.get("message", "{}")).get("message", {})
                method = msg.get("method")
                params = msg.get("params", {})
                if not method or not params:
                    continue
                if method == "Network.requestWillBeSent":
                    rid = params.get("requestId")
                    req = params.get("request", {})
                    rec = self._perf.setdefault(rid, {})
                    rec.update({
                        "url": req.get("url"),
                        "method": req.get("method"),
                        "type": params.get("type"),  # Document/XHR/FetchScript 등
                        "ts": params.get("timestamp"),
                    })
                elif method == "Network.responseReceived":
                    rid = params.get("requestId")
                    resp = params.get("response", {})
                    rec = self._perf.setdefault(rid, {})
                    rec.update({
                        "status": int(resp.get("status", 0)),
                        "mime": resp.get("mimeType"),
                        "proto": resp.get("protocol"),
                        "fromDiskCache": bool(resp.get("fromDiskCache", False)),
                        "fromServiceWorker": bool(resp.get("fromServiceWorker", False)),
                    })
                elif method == "Network.loadingFinished":
                    rid = params.get("requestId")
                    rec = self._perf.setdefault(rid, {})
                    rec["finished"] = True
                    rec["encoded"] = int(params.get("encodedDataLength", 0))
                elif method == "Network.loadingFailed":
                    rid = params.get("requestId")
                    rec = self._perf.setdefault(rid, {})
                    rec["failed"] = True
                    rec["errorText"] = params.get("errorText")
            except Exception:
                pass

    def _perf_is_first_party(self, url: str) -> bool:
        try:
            if not url:
                return False
            if url.startswith("/"):
                return True
            host = urlparse(url).hostname or ""
            return host.endswith(self.FIRST_PARTY_HOST)
        except Exception:
            return False

    def _perf_summary(self, tag: str):
        self._perf_ingest()
        stats = {
            "total": 0,
            "fp_total": 0, "fp_api_total": 0, "fp_api_2xx": 0, "fp_api_403": 0, "fp_api_4xx": 0, "fp_api_5xx": 0,
            "doc_status": None
        }
        samples_fp_api = []

        for rec in self._perf.values():
            url = rec.get("url")
            if not url:
                continue
            stats["total"] += 1
            if self._perf_is_first_party(url):
                stats["fp_total"] += 1
                if "/api/" in url:
                    stats["fp_api_total"] += 1
                    st = int(rec.get("status") or 0)
                    if 200 <= st < 300: stats["fp_api_2xx"] += 1
                    elif st == 403: stats["fp_api_403"] += 1
                    elif 400 <= st < 500: stats["fp_api_4xx"] += 1
                    elif st >= 500: stats["fp_api_5xx"] += 1
                    if len(samples_fp_api) < 8:
                        samples_fp_api.append({"url": url, "st": st, "type": rec.get("type")})
            if rec.get("type") == "Document" and stats["doc_status"] is None:
                try:
                    stats["doc_status"] = int(rec.get("status") or 0)
                except Exception:
                    pass

        print(f"[{tag} PERF] summary -> {stats}")
        if samples_fp_api:
            print(f"[{tag} PERF] fp_api samples ->")
            try:
                print(json.dumps(samples_fp_api, ensure_ascii=False))
            except Exception:
                print(samples_fp_api)
        return stats

    # ── Private: high-level summary & decisions ──────────────────────
    def _summary(self, tag: str):
        logs, net, cap, res, mem = self._read_tail()
        ck = self._cookie_names()

        cf_cookie = self._has_cf(ck)
        try:
            cf_challenge = any('/cdn-cgi/challenge-platform' in ((e.get('url') or '') if isinstance(e, dict) else '')
                               for e in net)
            deny_codes = {401, 403, 429, 503, 520, 1020}
            deny_hit = any(int(e.get('status') or 0) in deny_codes for e in net if isinstance(e, dict) and 'status' in e)
        except Exception:
            cf_challenge = False
            deny_hit = False

        cf = bool(cf_cookie or cf_challenge or deny_hit)

        print(f"[{tag}] current_url={self.driver.current_url}")
        print(f"[{tag}] cookies={ck}")
        print(f"[{tag}] cf_flags={cf} (cookie={cf_cookie}, challenge={cf_challenge}, deny_hit={deny_hit}) captcha={cap}")

        print(f"[{tag}] net_tail({len(net)}) ->")
        try: print(json.dumps(net, ensure_ascii=False))
        except Exception: print(net)

        print(f"[{tag}] res_tail({len(res)}) sample ->")
        try: print(json.dumps(res[-8:], ensure_ascii=False))
        except Exception: print(res[-8:])

        stats = self._summarize_network(net)
        print(f"[{tag}] net_summary -> {stats}")

        if cf_challenge:
            print(f"[{tag}] [CF] challenge flow detected in network events (/cdn-cgi/challenge-platform*)")

        if logs:
            print(f"[{tag}] console_tail({len(logs)})")
            for r in logs:
                print(f" - [{r.get('l')}] {r.get('m')}")

        if mem:
            print(f"[{tag}] perf_memory -> {mem}")

        return cf, cap, len(net), res, stats

    def _summarize_network(self, net_events):
        stats = {
            "total": len(net_events),
            "fp_total": 0, "fp_2xx": 0, "fp_403": 0, "fp_4xx": 0, "fp_5xx": 0, "fp_api": 0,
            "tp_total": 0, "tp_2xx": 0, "tp_4xx": 0, "tp_5xx": 0,
        }
        for e in net_events:
            if not isinstance(e, dict): continue
            url = (e.get('url') or '')
            status = int(e.get('status') or 0)
            is_fp = self._is_first_party(url)
            is_api = ("/api/" in url)
            if is_fp:
                stats["fp_total"] += 1
                if is_api: stats["fp_api"] += 1
                if 200 <= status < 300: stats["fp_2xx"] += 1
                elif status == 403: stats["fp_403"] += 1
                elif 400 <= status < 500: stats["fp_4xx"] += 1
                elif status >= 500: stats["fp_5xx"] += 1
            else:
                stats["tp_total"] += 1
                if 200 <= status < 300: stats["tp_2xx"] += 1
                elif 400 <= status < 500: stats["tp_4xx"] += 1
                elif status >= 500: stats["tp_5xx"] += 1
        return stats

    def _is_first_party(self, url: str) -> bool:
        try:
            if not url: return False
            if url.startswith("/"): return True
            host = urlparse(url).hostname or ""
            return host.endswith(self.FIRST_PARTY_HOST)
        except Exception:
            return False

    def _clear_origin(self):
        try:
            self.driver.execute_cdp_cmd("Storage.clearDataForOrigin", {
                "origin": self.ORIGIN,
                "storageTypes": "appcache,cookies,filesystem,indexeddb,localstorage,shadercache,websql,service_workers,cache_storage"
            })
            print("[RECOVER] origin storage cleared")
        except Exception as e:
            print(f"[RECOVER] clear 실패: {e}")

    def _humanize(self, scroll_px: int = 300, pause: float = 0.6):
        try:
            self.driver.execute_script(
                "window.scrollTo(0, Math.min(arguments[0], (document.body&&document.body.scrollHeight)||0));",
                int(scroll_px)
            )
        except Exception:
            pass
        time.sleep(pause)

    def _suspected_block(self, ok1: bool, ok2: bool, net1: int, net2: int, cf2: bool, cap2: bool, stats2: dict, pstats2: dict):
        suspected = False
        reasons = []
        if ok1 and not ok2:
            suspected = True; reasons.append("second_nav_dom_not_ready")
        if net2 == 0 and net1 > 0:
            suspected = True; reasons.append("no_network_events_on_second_nav")
        if cf2 or cap2:
            suspected = True; reasons.append("captcha_or_cloudflare_flags")
        # 1P API 403 비율 (in-page or perf 둘 중 하나라도)
        try:
            fp_api = int(stats2.get("fp_api", 0))
            fp_403 = int(stats2.get("fp_403", 0))
            if pstats2:
                fp_api = max(fp_api, int(pstats2.get("fp_api_total", 0)))
                fp_403 = max(fp_403, int(pstats2.get("fp_api_403", 0)))
            if fp_api >= 2 and (fp_403 / max(fp_api, 1)) >= 0.6:
                suspected = True; reasons.append("first_party_api_forbidden")
        except Exception:
            pass
        return suspected, reasons
