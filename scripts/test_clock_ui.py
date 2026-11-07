"""Native clock-panel layout/actions test. OCR source and touch input are simulated."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.request import Request,urlopen
import argparse,json,os,shutil,socket,subprocess,tempfile,threading,time
from playwright.sync_api import sync_playwright
from ui_touch_checks import choose,navigate,no_overflow
from ui_duration_presets import verify_duration_presets

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('binary');args=parser.parse_args()
root=Path(__file__).resolve().parents[1];binary=Path(args.binary).resolve();(root/'.test').mkdir(exist_ok=True)
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
def request(path,body=None):
    with urlopen(Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'}),timeout=4) as response:return json.load(response)
def wait(predicate):
    until=time.monotonic()+8
    while time.monotonic()<until:
        state=request('/api/state')
        if predicate(state):return state
        time.sleep(.05)
    raise AssertionError('State did not reach expected condition')
def set_clock(target,seconds,direction='down'):return request(f'/api/clock/{target}/set',{'seconds':seconds,'direction':direction})
class Source(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        assert self.path=='/json'
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
        self.wfile.write(json.dumps([{'name':'Time','text':'05:00','state':'Success'},{'name':'Shot Clock','text':'24','state':'Success'}]).encode())
source=ThreadingHTTPServer(('127.0.0.1',0),Source);threading.Thread(target=source.serve_forever,daemon=True).start()

with tempfile.TemporaryDirectory() as folder,sync_playwright() as p:
    config=Path(folder)/'config.json';log=(Path(folder)/'server.log').open('wb')
    def start():
        proc=subprocess.Popen([str(binary),'--config',str(config),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        for _ in range(100):
            try:request('/api/state');return proc
            except OSError:time.sleep(.05)
        raise AssertionError('Startup failed')
    proc=start();browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
    try:
        for width in (375,500,1000,1440,1920):
            set_clock('main',600);set_clock('shot',60)
            page=browser.new_page(viewport={'width':width,'height':1080},has_touch=width==375);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base);page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')")
            assert page.locator('footer').inner_text()=='Field Scoreboard · Free & open source · Windows & Linux'
            assert page.locator('#scoreboardDisplay #mainFormat,#scoreboardDisplay #shotFormat').count()==0
            assert page.locator('#scoreboardDisplay #homeFoulStyle,#scoreboardDisplay #awayFoulStyle,#scoreboardDisplay #foulDotsMax').count()==3
            dimensions=[];sets=[]
            for target in ('main','shot'):
                card=page.locator(f'.clock-card[data-clock={target}]');quick=card.locator('[data-clock-adjust]')
                assert quick.evaluate_all('els=>els.map(e=>e.dataset.clockAdjust)')==[f'{target}:{n}' for n in (-5,-1,1,5)]
                assert quick.all_inner_texts()==['−5s','−1s','+1s','+5s']
                assert card.evaluate("e=>e.lastElementChild.matches('.clock-set')")
                boxes=[card.locator(s).bounding_box() for s in ('.card-heading','.clock-reading','.clock-buttons','.clock-presets','.clock-setup','.clock-set')]
                for a,b in zip(boxes,boxes[1:]):assert a['y']+a['height']<=b['y']+1,(width,target,boxes)
                r=[b.bounding_box() for b in quick.all()];dimensions.append([(b['width'],b['height']) for b in r]);sets.append(boxes[-1])
                assert all(b['height']>=64 and b['width']>=72 for b in r)
                assert quick.evaluate_all('els=>els.every(e=>parseFloat(getComputedStyle(e).fontSize)>=22)')
                if width<=500:assert r[0]['y']==r[1]['y'] and r[2]['y']==r[3]['y'] and r[2]['y']>r[0]['y']
                else:assert len({b['y'] for b in r})==1
                assert abs(boxes[-1]['width']-boxes[2]['width'])<1 and boxes[-1]['height']>=72
                assert card.locator('.clock-setup h4').inner_text()=='Clock setup'
            assert dimensions[0]==dimensions[1],(width,dimensions)
            if width>=1000:assert abs(sets[0]['y']-sets[1]['y'])<1,'desktop Set buttons misaligned'
            assert page.evaluate("()=>document.getElementById('tab-control').lastElementChild.matches('.ocr-card')")
            assert page.locator('.both-clocks').bounding_box()['y']<page.locator('.clock-grid').bounding_box()['y']
            no_overflow(page);page.locator('.clock-grid').screenshot(path=str(root/f'.test/clocks15-{width}.png'))
            if width==1920:
                page.locator('.both-clocks').scroll_into_view_if_needed();page.screenshot(path=str(root/'.test/clocks15-maximized-1920x1080.png'))
            verify_duration_presets(page,request,wait,root,width)
            set_clock('main',600);set_clock('shot',60)
            # Actual click/tap/keyboard requests, every shortcut on both clocks.
            for state in ('paused','running') if width==1920 else ('paused',):
                request('/api/clock/both/start',{})
                if state=='paused':request('/api/clock/both/pause',{})
                for target in ('main','shot'):
                    for i,delta in enumerate((-5,-1,1,5)):
                        button=page.locator(f'[data-clock-adjust="{target}:{delta}"]');button.scroll_into_view_if_needed()
                        before=request('/api/state');started=time.monotonic()
                        with page.expect_response(lambda r:r.url.endswith(f'/api/clock/{target}/adjust') and r.request.method=='POST') as event:
                            if width==375:button.tap()
                            elif i%2:button.focus();page.keyboard.press('Enter')
                            else:button.click()
                        response=event.value;after=response.json();elapsed=time.monotonic()-started
                        assert response.ok and response.request.post_data_json=={'seconds':delta}
                        drift=before[target]['remaining_seconds']+delta-after[target]['remaining_seconds']
                        assert abs(drift)<.001 if state=='paused' else -.05<=drift<=elapsed+.15
                        other='shot' if target=='main' else 'main'
                        assert after[target]['state']==state and after[other]['state']==state
                        if state=='paused':assert after[other]==before[other]
            request('/api/clock/both/pause',{}) if request('/api/state')['main']['state']=='running' else None
            # Setup drafts and one-unit steppers never invoke Set implicitly.
            set_clock('main',600);set_clock('shot',60);page.wait_for_function("()=>document.getElementById('mainMinutes').value==='10'")
            before=request('/api/state');page.locator('#mainMinutes').fill('0');page.locator('#mainSeconds').fill('20');page.locator('#shotSeconds').fill('17')
            for id in ('mainMinutes','mainSeconds','shotSeconds'):
                n=int(page.locator('#'+id).input_value());page.locator(f'[data-step-input="{id}:1"]').click();assert int(page.locator('#'+id).input_value())==n+1
                page.locator(f'[data-step-input="{id}:-1"]').click();assert int(page.locator('#'+id).input_value())==n
            choose(page,'mainDirection','up');choose(page,'mainFormat','SS');choose(page,'shotFormat','SS.t')
            page.wait_for_function("()=>document.getElementById('displayStatus').textContent===''")
            navigate(page,'editor');navigate(page,'control');page.wait_for_timeout(600)
            now=request('/api/state');assert now['main']['duration_seconds']==600 and now['main']['direction']=='down' and now['shot']['duration_seconds']==60
            assert now['layout']['main_clock_format']=='SS' and now['layout']['shot_clock_format']=='SS.t'
            assert page.locator('#mainMinutes').input_value()=='0' and page.locator('#mainSeconds').input_value()=='20' and page.locator('#shotSeconds').input_value()=='17'
            page.locator('[data-clock-set=main]').click();wait(lambda s:s['main']['duration_seconds']==20 and s['main']['direction']=='up')
            page.locator('[data-clock-set=shot]').click();wait(lambda s:s['shot']['duration_seconds']==17)
            # Failed Set leaves current values; valid zero-minute duration works.
            before=request('/api/state');page.locator('#shotSeconds').fill('3601');page.locator('[data-clock-set=shot]').click()
            page.locator('#mainMinutes').fill('10080');page.locator('#mainSeconds').fill('1');page.locator('[data-clock-set=main]').click()
            assert request('/api/state')['main']==before['main'] and request('/api/state')['shot']==before['shot']
            assert not errors,errors;page.close();print('Clock layout/actions/setup/format/footer:',width,'PASS',flush=True)
        # OCR owns time actions only; appearance choices remain available.
        request('/api/ocr/connect',{'address':f'http://127.0.0.1:{source.server_port}'});wait(lambda s:s['ocr']['targets']['shot']['can_follow'])
        page=browser.new_page();page.goto(base);page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')")
        for target,format_id,value in [('main','mainFormat','MM:SS'),('shot','shotFormat','MM:SS')]:
            request('/api/ocr/follow',{'target':target});page.wait_for_function('(t)=>document.querySelector(`[data-clock-set="${t}"]`).disabled',arg=target)
            assert page.locator(f'[data-clock-adjust^="{target}:"]').evaluate_all('els=>els.length===4&&els.every(e=>e.disabled)')
            assert page.locator('[data-clock-action="both:start"]').is_disabled()
            if target=='main':
                before=request('/api/state');page.locator('[data-main-duration="8"]').click();page.wait_for_timeout(550)
                assert page.locator('#mainMinutes').input_value()=='8' and page.locator('#mainSeconds').input_value()=='0'
                assert page.locator('[data-clock-set=main]').is_disabled()
                after=request('/api/state');assert after['main']==before['main'] and after['shot']==before['shot']
                assert after['ocr']['targets']['main']['following'] and after['main']['duration_seconds']==before['main']['duration_seconds']
            held=request('/api/state')[target];choose(page,format_id,value);page.wait_for_function("()=>document.getElementById('displayStatus').textContent===''")
            actual=request('/api/state')[target];assert actual['state']=='ocr' and actual['remaining_seconds']==held['remaining_seconds']
            request('/api/ocr/manual',{'target':target});page.wait_for_function('(t)=>!document.querySelector(`[data-clock-set="${t}"]`).disabled',arg=target)
            assert request('/api/state')[target]['state']=='paused'
        # Existing conditional shot reset/presets remain immediate.
        set_clock('main',600);request('/api/clock/main/start',{})
        for seconds in (14,24,30):
            page.locator(f'[data-shot-preset="{seconds}"]').click();wait(lambda s:s['shot']['duration_seconds']==seconds and s['shot']['state']=='running')
        page.locator('[data-clock-action="main:pause"]').click();wait(lambda s:s['main']['state']=='paused')
        page.locator('[data-clock-action="shot:reset"]').click();wait(lambda s:s['shot']['state']=='ready')
        page.locator('label.shot-auto-hide').click();wait(lambda s:s['shot_auto_hide'])
        page.locator('#shotAutoHide').focus()
        with page.expect_response(lambda r:r.url.endswith('/api/game') and r.request.method=='POST') as toggle:
            page.keyboard.press('Space')
        assert not toggle.value.json()['shot_auto_hide'];wait(lambda s:not s['shot_auto_hide'])
        # Let the browser consume the first response before another toggle.
        page.wait_for_timeout(150)
        with page.expect_response(lambda r:r.url.endswith('/api/game') and r.request.method=='POST') as toggle:
            page.keyboard.press('Space')
        assert toggle.value.json()['shot_auto_hide'];wait(lambda s:s['shot_auto_hide'])
        final=request('/api/state');proc.terminate();proc.wait(timeout=5);proc=start();after=request('/api/state')
        for key in ('main_clock_format','shot_clock_format'):assert after['layout'][key]==final['layout'][key]
        assert after['shot_auto_hide'] and after['main']['state']==after['shot']['state']=='ready'
        print('Clock OCR guards, immediate formats, presets/reset, auto-hide and restart PASS',flush=True)
    finally:browser.close();proc.terminate();proc.wait(timeout=5);log.close();source.shutdown();source.server_close()
