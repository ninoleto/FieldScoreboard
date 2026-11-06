"""Native ScoreSight integration regression; --ui adds Chromium, --live-address reads a real source.

Always uses an isolated Field Scoreboard config/port. Never changes the OCR source.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse, json, os, shutil, socket, subprocess, tempfile, threading, time
import urllib.request

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('binary')
parser.add_argument('--ui',action='store_true')
parser.add_argument('--live-address')
args=parser.parse_args()
if args.ui and args.live_address:parser.error('--ui uses simulated fields; run live observations separately')
root=Path(__file__).resolve().parents[1]
binary=Path(args.binary).resolve()
(root/'.test').mkdir(exist_ok=True)
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'

def request(path,body=None):
    data=None if body is None else json.dumps(body).encode()
    with urllib.request.urlopen(urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'}),timeout=3) as response:
        return json.load(response)

def wait_for(predicate,timeout=5):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        state=request('/api/state')
        if predicate(state):return state
        time.sleep(.05)
    raise AssertionError('Timed out: '+json.dumps(state.get('ocr',{})))

fixture={'text':'12:34','state':'SameNoChange','status':200,'missing':False,'extra':False}
class Source(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        assert self.path=='/json' and self.headers.get('Authorization') is None
        state=fixture.copy()
        payload=[] if state['missing'] else [{'name':'Time','text':state['text'],'state':state['state'],'rect':{'x':1,'y':2,'width':100,'height':50}}]
        # Other fields intentionally look usable but must never be applied.
        payload += [{'name':'Home Score','text':'999','state':'Success'},{'name':'Shot Clock','text':'00:01','state':'Success'}]
        if state['extra']:payload.append({'name':'Alternate','text':'03:21','state':'Success'})
        self.send_response(state['status']);self.send_header('Content-Type','application/json');self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

source=ThreadingHTTPServer(('127.0.0.1',0),Source)
threading.Thread(target=source.serve_forever,daemon=True).start()
address=args.live_address or f'http://127.0.0.1:{source.server_port}'

with tempfile.TemporaryDirectory() as folder:
    config=Path(folder)/'config.json'
    with (Path(folder)/'server.log').open('wb') as log:
        def start():
            process=subprocess.Popen([str(binary),'--config',str(config),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            for _ in range(80):
                try:request('/api/state');return process
                except OSError:time.sleep(.05)
            raise AssertionError('Native test process did not start')
        proc=start()
        try:
            original=request('/api/state')
            request('/api/ocr/connect',{'address':address})
            state=wait_for(lambda s:s['ocr']['can_follow'])
            assert state['ocr']['field']=='Time' and state['main']==original['main']
            assert state['ocr']['freshness']=='unavailable' and state['ocr']['warning']
            request('/api/ocr/follow',{})
            state=wait_for(lambda s:s['main']['state']=='ocr')
            if args.live_address:
                values=[];statuses=set()
                for _ in range(40):
                    state=request('/api/state');values.append(state['main']['display']);statuses.add(state['ocr']['detection_state'])
                    assert state['main']['state']=='ocr' and state['ocr']['following']
                    time.sleep(.2)
                print('LIVE observation:',json.dumps({'samples':len(values),'distinct_values':len(set(values)),'first':values[0],'last':values[-1],'states':sorted(statuses),'fields':state['ocr']['fields'],'freshness':state['ocr']['freshness']}))
            else:
                for text in ('12:33','12:33','20:00','00:00','04:59'):
                    fixture['text']=text
                    wait_for(lambda s:s['main']['display']==text)
                time.sleep(1.2)
                assert request('/api/state')['main']['display']=='04:59','independent countdown during source pause'
                for update,reading in [({'text':'00:00','state':'FailedFilter'},'rejected'),({'text':'','state':'Empty'},'rejected'),({'text':'99:99','state':'Success'},'malformed'),({'missing':True},'missing'),({'status':503},'unavailable')]:
                    fixture.update(update)
                    state=wait_for(lambda s:s['ocr']['reading']==reading)
                    assert state['main']['display']=='04:59' and state['ocr']['warning']
                fixture.update(text='00:20',state='Success',missing=False,status=200)
                wait_for(lambda s:s['main']['display']=='00:20')
                request('/api/game',{'field':'shot_auto_hide','value':True})
                assert not request('/api/state')['shot_visible']
                fixture['text']='00:30';wait_for(lambda s:s['shot_visible'])
                assert 'ocr' not in request('/api/overlay-state')
                assert request('/api/overlay-state')['main']['display']==request('/api/state')['main']['display']
            manual=request('/api/ocr/manual',{})
            held=manual['main']['display']
            assert manual['main']['state']=='paused'
            if not args.live_address:fixture['text']='00:01'
            time.sleep(1.1)
            state=request('/api/state')
            assert state['main']['display']==held and not state['ocr']['following']
            for key in ('home_score','away_score','home_fouls','away_fouls','period','period_overtime','home_name','away_name','shot'):
                assert state[key]==original[key],('unrelated field changed',key)
            print(('LIVE' if args.live_address else 'SIMULATED')+': check/follow, last-value hold, takeover and unrelated fields PASS')
            if args.ui:
                from playwright.sync_api import sync_playwright
                from ui_touch_checks import choose,navigate,no_overflow
                with sync_playwright() as p:
                    executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
                    browser=p.chromium.launch(headless=True,executable_path=executable)
                    try:
                        for width in (375,500,1000,1440,1920):
                            context=browser.new_context(viewport={'width':width,'height':1080},has_touch=width==375)
                            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                            page.goto(base);page.wait_for_function("()=>document.getElementById('ocrConnection').textContent==='Connected to ScoreSight'")
                            assert page.locator('#ocrField').is_hidden()
                            page.locator('#ocrAddress').fill('http://127.0.0.1:')
                            navigate(page,'editor');navigate(page,'control');page.wait_for_timeout(600)
                            assert page.locator('#ocrAddress').input_value()=='http://127.0.0.1:'
                            assert page.locator('#ocrFollow').is_disabled()
                            page.locator('#ocrAddress').fill(address);page.locator('#ocrConnect').click()
                            page.wait_for_function("()=>!document.getElementById('ocrFollow').disabled")
                            fixture['extra']=True
                            page.wait_for_function("()=>[...document.getElementById('ocrField').options].some(o=>o.value==='Alternate')")
                            page.locator('#ocrFieldChoice').click();page.keyboard.press('Escape')
                            assert page.locator('#ocrFieldChoice').evaluate('e=>e===document.activeElement')
                            choose(page,'ocrField','Alternate')
                            page.wait_for_function("()=>document.getElementById('ocrRecognized').textContent==='03:21'")
                            choose(page,'ocrField','Time')
                            page.wait_for_function("()=>!document.getElementById('ocrFollow').disabled")
                            page.locator('#ocrFollow').focus();page.keyboard.press('Enter')
                            page.wait_for_function("()=>document.getElementById('ocrMode').textContent==='FOLLOWING OCR'")
                            assert page.locator('[data-clock-action="main:start"]').is_disabled()
                            assert page.locator('[data-clock-action="both:start"]').is_disabled()
                            assert page.locator('[data-clock-action="shot:start"]').is_enabled()
                            assert page.locator('#ocrFollow').get_attribute('aria-pressed')=='true'
                            for id in ('ocrConnect','ocrFieldChoice','ocrFollow','ocrManual','ocrAddress'):
                                assert page.locator('#'+id).bounding_box()['height']>=60,(width,id)
                            assert page.evaluate('new Set([...document.querySelectorAll("[id]")].map(e=>e.id)).size===document.querySelectorAll("[id]").length')
                            no_overflow(page)
                            page.locator('#ocrHeading').scroll_into_view_if_needed()
                            page.screenshot(path=str(root/f'.test/ocr-{width}.png'),full_page=True)
                            page.locator('.ocr-card').screenshot(path=str(root/f'.test/ocr-panel-{width}.png'))
                            if width==1920:page.screenshot(path=str(root/'.test/ocr-maximized-1920x1080.png'))
                            if width==375:page.locator('#ocrManual').tap()
                            else:page.locator('#ocrManual').focus();page.keyboard.press('Space')
                            page.wait_for_function("()=>document.getElementById('mainState').textContent==='PAUSED'")
                            assert page.locator('[data-clock-action="main:start"]').is_enabled()
                            assert not errors,errors
                            print('OCR dynamic field dialog, drafts, keyboard/touch and geometry:',width,'PASS')
                            context.close()
                    finally:browser.close()
            proc.terminate();proc.wait(timeout=5);proc=start()
            restarted=request('/api/state')
            assert restarted['ocr']['connection']=='disconnected' and not restarted['ocr']['following'] and restarted['main']['state']=='ready'
            assert restarted['ocr']['address']==address
            print('OCR restart: settings retained, manual Ready, no automatic connection/follow PASS')
        finally:
            proc.terminate();proc.wait(timeout=5)
source.shutdown();source.server_close()
