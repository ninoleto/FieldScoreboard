"""Native display preferences, editor toolbar/order and draft-isolation checks."""
from pathlib import Path
import argparse,json,os,shutil,socket,subprocess,tempfile,time
from urllib.request import Request,urlopen
from playwright.sync_api import sync_playwright
from ui_touch_checks import choose,navigate,no_overflow

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('binary');args=parser.parse_args()
root=Path(__file__).resolve().parents[1];binary=Path(args.binary).resolve();(root/'.test').mkdir(exist_ok=True)
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
def request(path,body=None,method=None):
    with urlopen(Request(base+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Content-Type':'application/json'}),timeout=4) as response:return json.load(response)
def number(page,id,n):page.locator('#'+id).fill(str(n));page.locator('#'+id).blur()
def settled(page):page.wait_for_function("()=>document.getElementById('displayStatus').textContent===''")
def save(page):page.locator('#saveLayout').click();page.wait_for_function("()=>document.getElementById('unsavedBadge').classList.contains('hidden')&&!document.getElementById('saveLayout').disabled")
def prefs(s):return {k:s['layout'][k] for k in ('foul_style_home','foul_style_away','foul_dots_max','main_clock_format','shot_clock_format')}
def game(s):
    return {k:v for k,v in s.items() if k in ('home_score','away_score','home_fouls','away_fouls','period','period_format','period_overtime','period_label')}|{k:{f:v for f,v in s[k].items() if f!='display'} for k in ('main','shot')}

with tempfile.TemporaryDirectory() as folder,sync_playwright() as p:
    config=Path(folder)/'config.json';log=(Path(folder)/'server.log').open('wb')
    def start():
        process=subprocess.Popen([str(binary),'--config',str(config),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        for _ in range(100):
            try:request('/api/state');return process
            except OSError:time.sleep(.05)
        raise AssertionError('Startup failed')
    proc=start();browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
    try:
        for field,value in [('home_score',17),('away_score',23),('home_fouls',6),('away_fouls',4),('period',3),('period_format','quarter')]:request('/api/game',{'field':field,'value':value})
        original=game(request('/api/state'));order=['main_clock','shot_clock','period','home_name','home_score','home_fouls','away_name','away_score','away_fouls']
        for width in (375,500,1000,1440,1920):
            page=browser.new_page(viewport={'width':width,'height':1080},has_touch=width==375);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base);page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')")
            assert page.locator('#displayHeading').inner_text()=='Foul indicators'
            assert page.locator('#scoreboardDisplay h4').count()==0
            assert page.locator('#scoreboardDisplay > .note').first.inner_text()=='Changes appear immediately in the preview and OBS.'
            assert page.locator('footer').inner_text()=='Field Scoreboard · Free & open source · Windows & Linux'
            assert page.locator('.version').inner_text()=='v0.1.0'
            page.on('dialog',lambda d:d.accept())
            def rect(selector):return page.locator(selector).bounding_box()
            assert page.evaluate("()=>document.getElementById('tab-control').lastElementChild.matches('.ocr-card')")
            d=rect('#scoreboardDisplay');preview=rect('#livePreview')
            if width>=1440:assert abs(d['x']-preview['x'])<1 and abs(d['width']-preview['width'])<1 and 15<=d['y']-preview['y']-preview['height']<=30
            else:assert d['y']>=rect('.clock-grid')['y']+rect('.clock-grid')['height']
            assert d['y']+d['height']<rect('.ocr-card')['y'];no_overflow(page)
            page.screenshot(path=str(root/f'.test/display14-live-{width}.png'),full_page=True)
            if width==1920:page.screenshot(path=str(root/'.test/display14-maximized-1920x1080.png'))
            navigate(page,'editor');assert page.locator('#tab-editor #mainFormat,#tab-editor #homeFoulStyle').count()==0
            pills=page.locator('#fieldPills button');assert pills.evaluate_all('els=>els.map(e=>e.dataset.field)')==order
            pills.first.focus()
            for i,id in enumerate(order):
                assert page.evaluate('document.activeElement.dataset.field')==id
                assert pills.nth(i).bounding_box()['height']>=64
                if i<len(order)-1:page.keyboard.press('Tab')
            a=rect('#freeTransform');b=rect('#selectBackground');label=rect('#editorSelectionLabel');help=rect('#editorModeHelp')
            assert a['height']==b['height'] and a['height']>=80
            if width<=720:assert b['y']>=a['y']+a['height']
            else:assert a['x']<b['x'] and abs(a['y']-b['y'])<1 and abs(a['width']-b['width'])<1
            assert label['y']+label['height']<=a['y'] and help['y']>=b['y']+b['height']
            assert 'Select an element' in page.locator('#editorModeHelp').inner_text()
            button=page.locator('#freeTransform')
            if width==375:button.tap()
            else:button.focus();page.keyboard.press('Space')
            assert button.inner_text()=='Done transforming' and 'Done transforming keeps your draft' in page.locator('#editorModeHelp').inner_text()
            page.locator('[data-field=home_score]').click();assert button.inner_text()=='Free transform'
            assert page.locator('.element-resize-handle:visible').count()==0
            number(page,'elementX',700+width//10)
            draft=page.locator('#elementX').input_value();saved_x=request('/api/state')['layout']['elements']['home_score']['x']
            navigate(page,'control')
            for id,value in [('homeFoulStyle','number'),('awayFoulStyle','number'),('mainFormat','HH:MM:SS'),('shotFormat','MM:SS')]:choose(page,id,value);settled(page)
            number(page,'foulDotsMax',9);settled(page)
            assert request('/api/state')['layout']['elements']['home_score']['x']==saved_x
            assert game(request('/api/state'))==original
            overlay=browser.new_page(viewport={'width':1920,'height':1080});overlay.goto(base+'/overlay');overlay.wait_for_selector('.stage-element');page.bring_to_front()
            for target,text in [('home_fouls','6'),('away_fouls','4'),('main_clock','00:20:00'),('shot_clock','00:24')]:
                page.wait_for_function('([id,text])=>document.querySelector(`#previewStage [data-id="${id}"]`).textContent===text',arg=[target,text])
                overlay.wait_for_function('([id,text])=>document.querySelector(`#overlayStage [data-id="${id}"]`).textContent===text',arg=[target,text],polling=100)
            overlay.close();navigate(page,'editor');assert page.locator('#elementX').input_value()==draft
            current=prefs(request('/api/state'));save(page);assert prefs(request('/api/state'))==current
            number(page,'elementX',1200);navigate(page,'control');choose(page,'homeFoulStyle','dots');settled(page)
            # Invalid/unfinished live numeric input survives updates and does not block layout Save.
            page.locator('#foulDotsMax').fill('');page.locator('#foulDotsMax').blur();page.wait_for_timeout(500);assert page.locator('#foulDotsMax').input_value()==''
            navigate(page,'editor');save(page);assert request('/api/state')['layout']['elements']['home_score']['x']==1200
            number(page,'elementX',1300);navigate(page,'control');choose(page,'mainFormat','M:SS');settled(page);navigate(page,'editor')
            current=prefs(request('/api/state'));page.locator('#discardLayout').click();assert prefs(request('/api/state'))==current and page.locator('#elementX').input_value()=='1200'
            page.locator('#resetPositions').click();save(page);assert prefs(request('/api/state'))==current
            no_overflow(page);page.screenshot(path=str(root/f'.test/display14-editor-{width}.png'),full_page=True)
            assert not errors,errors;page.close();print('Display/toolbar/order/drafts/OBS:',width,'PASS',flush=True)
        page=browser.new_page();page.goto(base);page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')");page.on('dialog',lambda d:d.accept())
        navigate(page,'editor');page.locator('[data-field=home_score]').click();number(page,'elementX',811)
        # Another operator changes display while this editor draft remains open.
        request('/api/display',{'field':'foul_dots_max','value':12});save(page)
        assert request('/api/state')['layout']['foul_dots_max']==12 and request('/api/state')['layout']['elements']['home_score']['x']==811
        page.locator('#profileName').fill('Display test');page.locator('#saveProfile').click()
        page.wait_for_function("()=>[...document.getElementById('profileSelect').options].some(o=>o.value==='Display test')")
        saved_preferences=prefs(request('/api/state'));navigate(page,'control');number(page,'foulDotsMax',3);settled(page)
        navigate(page,'editor');choose(page,'profileSelect','Display test');page.locator('#loadProfile').click()
        page.wait_for_function("()=>document.getElementById('foulDotsMax').value==='12'")
        assert prefs(request('/api/state'))==saved_preferences and game(request('/api/state'))==original
        # Delay a display response: Save waits, retains geometry and the queued preferences.
        page.evaluate("""()=>{const displayFetch=window.fetch;window.fetch=async(...args)=>{const r=await displayFetch(...args);if(args[0]==='/api/display'&&window.holdDisplay){window.holdDisplay=false;await new Promise(resolve=>{window.releaseDisplay=resolve;window.displayHeld=true})}return r}}""")
        number(page,'elementX',844);navigate(page,'control');page.evaluate('window.holdDisplay=true');choose(page,'shotFormat','SS.t');page.wait_for_function('()=>window.displayHeld')
        choose(page,'mainFormat','SS');navigate(page,'editor');page.locator('#saveLayout').click();assert page.locator('#unsavedBadge').is_visible()
        page.evaluate('window.releaseDisplay()');page.wait_for_function("()=>document.getElementById('unsavedBadge').classList.contains('hidden')")
        final=request('/api/state');assert final['layout']['elements']['home_score']['x']==844 and final['layout']['main_clock_format']=='SS' and final['layout']['shot_clock_format']=='SS.t'
        assert game(final)==original
        proc.terminate();proc.wait(timeout=5);proc=start();assert prefs(request('/api/state'))==prefs(final)
        print('External update/stale draft, presets, delayed writes, state isolation and restart PASS',flush=True)
    finally:browser.close();proc.terminate();proc.wait(timeout=5);log.close()
