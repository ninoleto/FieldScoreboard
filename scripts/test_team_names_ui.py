"""Live team-name sizing and active-edit protection; native app, simulated OCR."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.request import Request,urlopen
import argparse,json,os,shutil,socket,subprocess,tempfile,threading,time
from playwright.sync_api import sync_playwright
from ui_touch_checks import no_overflow

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
    raise AssertionError('Expected state not reached')
class Source(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
        self.wfile.write(json.dumps([{'name':name,'text':value,'state':'Success'} for name,value in [('Home Score','27'),('Away Score','35'),('Home Fouls','3'),('Away Fouls','4')]]).encode())
source=ThreadingHTTPServer(('127.0.0.1',0),Source);threading.Thread(target=source.serve_forever,daemon=True).start()
def typography(page,stage,key):
    return page.locator(f'#{stage} [data-id={key}]').evaluate('e=>[e.style.fontFamily,e.style.fontSize,e.style.fontWeight,e.style.left,e.style.top,e.style.transform,e.dataset.align]')
with tempfile.TemporaryDirectory() as folder,sync_playwright() as p:
    config=Path(folder)/'config.json';log=(Path(folder)/'server.log').open('wb')
    proc=subprocess.Popen([str(binary),'--config',str(config),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    browser=None
    try:
        for _ in range(100):
            try:initial=request('/api/state');break
            except OSError:time.sleep(.05)
        else:raise AssertionError('Startup failed')
        request('/api/ocr/connect',{'address':f'http://127.0.0.1:{source.server_port}'})
        targets=['home_score','away_score','home_fouls','away_fouls']
        wait(lambda s:all(s['ocr']['targets'][t]['can_follow'] for t in targets))
        for target in targets:request('/api/ocr/follow',{'target':target})
        wait(lambda s:all(s['ocr']['targets'][t]['following'] for t in targets))
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
        overlay=browser.new_page(viewport={'width':1920,'height':1080});overlay.goto(base+'/overlay');overlay.wait_for_selector('.stage-element')
        saved_layout=request('/api/state')['layout']
        for width in (375,500,1000,1440,1920):
            page=browser.new_page(viewport={'width':width,'height':1080},has_touch=width==375);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base);page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')")
            for team in ('home','away'):
                id=team+'Name';key=team+'_name';field=page.locator('#'+id);label=page.locator(f'label[for={id}]')
                assert field.is_enabled() and field.get_attribute('maxlength')=='32'
                assert page.locator(f'[data-adjust="{team}_score:1"]').is_disabled() and page.locator(f'[data-adjust="{team}_fouls:1"]').is_disabled()
                assert label.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)>=20&&parseFloat(getComputedStyle(e).fontSize)<=22&&Number(getComputedStyle(e).fontWeight)>=700')
                assert field.evaluate('e=>e.getBoundingClientRect().height>=64&&parseFloat(getComputedStyle(e).fontSize)>=24&&parseFloat(getComputedStyle(e).paddingLeft)>=12')
                assert field.evaluate('e=>Math.abs(e.getBoundingClientRect().width-(e.parentElement.clientWidth-parseFloat(getComputedStyle(e.parentElement).paddingLeft)-parseFloat(getComputedStyle(e.parentElement).paddingRight)))<1')
                a,b,c=label.bounding_box(),field.bounding_box(),field.locator('..').locator('.score-foul-row').bounding_box()
                assert b['y']-a['y']-a['height']>=10 and c['y']-b['y']-b['height']>=18
                original=typography(overlay,'overlayStage',key);before=request('/api/state')[key]
                if width==375:field.tap()
                else:label.click()
                assert field.evaluate('e=>e===document.activeElement')
                assert field.evaluate('e=>getComputedStyle(e).borderColor')=='rgb(139, 193, 255)'
                field.fill(team.title()+' Draft Team');field.evaluate('e=>e.setSelectionRange(3,8)')
                # Real backend changes arrive through polling while a selection/caret is active.
                request('/api/game',{'field':key,'value':team.title()+' Remote Update'})
                page.wait_for_timeout(1100)
                assert field.input_value()==team.title()+' Draft Team'
                assert field.evaluate('e=>[e.selectionStart,e.selectionEnd,e===document.activeElement]')==[3,8,True]
                assert request('/api/state')[key]==team.title()+' Remote Update'
                page.keyboard.insert_text('X');draft=field.input_value();caret=field.evaluate('e=>e.selectionStart')
                page.wait_for_timeout(700);assert field.input_value()==draft and field.evaluate('e=>e.selectionStart')==caret
                with page.expect_response(lambda r:r.url.endswith('/api/game') and r.request.method=='POST') as event:page.keyboard.press('Tab')
                assert event.value.ok and event.value.request.post_data_json=={'field':key,'value':draft}
                wait(lambda s:s[key]==draft)
                # Browser max length and ordinary keyboard entry retain the existing 32-character limit.
                field.focus();page.keyboard.press('Control+A');page.keyboard.insert_text(team[0].upper()*40)
                assert field.input_value()==team[0].upper()*32
                long_name=field.input_value();page.wait_for_timeout(600);assert field.input_value()==long_name
                with page.expect_response(lambda r:r.url.endswith('/api/game') and r.request.method=='POST') as event:page.keyboard.press('Tab')
                assert event.value.ok;wait(lambda s:s[key]==long_name)
                overlay.wait_for_function('a=>document.querySelector(`#overlayStage [data-id=${a[0]}]`).textContent===a[1]',arg=[key,long_name])
                assert typography(overlay,'overlayStage',key)==original and request('/api/state')['layout']==saved_layout
                page.wait_for_function('a=>document.querySelector(`#previewStage [data-id=${a[0]}]`).textContent===a[1]',arg=[key,long_name])
                assert typography(page,'previewStage',key)==original
                field.fill('   ');page.keyboard.press('Tab');assert 'Team name cannot be empty' in page.locator('#banner').inner_text()
                assert request('/api/state')[key]==long_name
                field.fill('  '+team.title()+' Team  ')
                with page.expect_response(lambda r:r.url.endswith('/api/game') and r.request.method=='POST') as event:page.keyboard.press('Tab')
                assert event.value.ok;wait(lambda s:s[key]==team.title()+' Team')
                assert all(request('/api/state')['ocr']['targets'][t]['following'] for t in targets)
                no_overflow(page)
            page.locator('.match-card').screenshot(path=str(root/f'.test/team-names17-{width}.png'))
            if width==1920:page.evaluate('scrollTo(0,0)');page.screenshot(path=str(root/'.test/teams17-maximized-1920x1080.png'))
            assert not errors,errors;page.close()
            print('Team fields: sizing, mouse/touch/keyboard, caret/polling, length/validation, OCR availability, unchanged overlay typography:',width,'PASS',flush=True)
    finally:
        if browser:browser.close()
        proc.terminate();proc.wait(timeout=5);log.close();source.shutdown();source.server_close()
