"""Native Font-picker weight/draft/rendering regression with isolated settings."""
from pathlib import Path
from urllib.request import Request,urlopen
import argparse,json,os,shutil,socket,subprocess,tempfile,time
from playwright.sync_api import sync_playwright
from ui_touch_checks import choose,navigate,no_overflow

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('binary');args=parser.parse_args()
root=Path(__file__).resolve().parents[1];binary=Path(args.binary).resolve();(root/'.test').mkdir(exist_ok=True)
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
def request(path,body=None,method=None):
    with urlopen(Request(base+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Content-Type':'application/json'}),timeout=4) as response:return json.load(response)
def save(page):
    page.locator('#saveLayout').click();page.wait_for_function("()=>document.getElementById('unsavedBadge').classList.contains('hidden')&&!document.getElementById('saveLayout').disabled")
def style(page,stage,id='home_name'):
    return page.locator(f'#{stage} [data-id={id}]').evaluate('e=>({font:e.style.fontFamily,weight:e.style.fontWeight,transform:e.style.transform})')
def geometry(page,stage):return page.evaluate('s=>FieldStage.elementBox(document.getElementById(s),"home_name")',stage)

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
        original=request('/api/state')['layout'];original['elements']['home_name'].update(font='sans',bold=False,transform={'scale_x':1.35,'scale_y':.8,'lock_aspect':False})
        for width in (375,500,1000,1440,1920):
            request('/api/layout',original,'PUT')
            page=browser.new_page(viewport={'width':width,'height':1080},has_touch=width==375);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base);page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')");navigate(page,'editor');page.locator('[data-field=home_name]').click()
            overlay=browser.new_page(viewport={'width':1920,'height':1080});overlay.goto(base+'/overlay');overlay.wait_for_selector('.stage-element');page.bring_to_front()
            initial=style(overlay,'overlayStage');saved_element=request('/api/state')['layout']['elements']['home_name']
            assert page.locator('.inspector #elementBold,input#elementBold').count()==0
            choose(page,'elementFont','serif');assert 'Serif · Regular' in page.locator('#elementFontChoice').inner_text()
            page.locator('#elementFontChoice').click();switch=page.locator('#elementBold')
            assert switch.get_attribute('role')=='switch' and switch.get_attribute('aria-checked')=='false'
            assert switch.bounding_box()['height']>=64 and switch.bounding_box()['width']>=200
            assert page.locator('#touchChoiceList #elementBold').count()==0 and page.locator('#touchChoiceList [role=option]').count()==4
            if width==375:switch.tap()
            else:switch.focus();page.keyboard.press('Space')
            assert page.locator('#touchChoiceDialog').is_visible() and switch.get_attribute('aria-checked')=='true'
            assert page.locator('#elementFont').input_value()=='serif';page.wait_for_timeout(550)
            assert style(page,'editorStage')['weight']=='800' and request('/api/state')['layout']['elements']['home_name']==saved_element
            assert style(overlay,'overlayStage')==initial and style(page,'previewStage')==initial
            page.keyboard.press('Escape');assert page.locator('#elementFontChoice').evaluate('e=>e===document.activeElement')
            assert 'Serif · Bold' in page.locator('#elementFontChoice').inner_text()
            choose(page,'elementFont','mono');assert 'Monospace · Bold' in page.locator('#elementFontChoice').inner_text()
            choose(page,'elementFont','serif');page.locator('#elementFontChoice').click();switch.click();assert switch.get_attribute('aria-checked')=='false'
            assert page.locator('#elementFont').input_value()=='serif';switch.focus();page.keyboard.press('Enter');assert switch.get_attribute('aria-checked')=='true'
            # At short/zoom-sized viewports the list scrolls, while Bold stays fixed.
            page.set_viewport_size({'width':width,'height':300});before=switch.bounding_box();listing=page.locator('#touchChoiceList');listing.hover();page.mouse.wheel(0,220);page.wait_for_timeout(200)
            assert listing.evaluate('e=>e.scrollTop')>0 and abs(switch.bounding_box()['y']-before['y'])<1
            assert switch.bounding_box()['y']>=0 and switch.bounding_box()['y']+switch.bounding_box()['height']<=300
            assert page.locator('#elementFont').input_value()=='serif' and switch.get_attribute('aria-checked')=='true'
            no_overflow(page);page.screenshot(path=str(root/f'.test/font16-short-{width}.png'))
            switch.focus();page.keyboard.press('Tab');assert page.locator('#touchChoiceList [role=option]:focus').count()==1
            page.keyboard.press('Tab');assert page.locator('#touchChoiceClose').evaluate('e=>e===document.activeElement')
            page.keyboard.press('Tab');assert switch.evaluate('e=>e===document.activeElement')
            page.keyboard.press('Escape');page.set_viewport_size({'width':width,'height':1080})
            # A different picker must have no Bold control/tab stop.
            page.locator('#elementAlignChoice').click();assert switch.is_hidden()
            for _ in range(4):page.keyboard.press('Tab');assert page.locator('#elementBold').evaluate('e=>e!==document.activeElement')
            page.keyboard.press('Escape')
            page.locator('[data-field=away_name]').click();choose(page,'elementFont','heavy');page.locator('#elementFontChoice').click()
            if switch.get_attribute('aria-checked')=='true':switch.click()
            page.keyboard.press('Escape');assert 'Heavy display · Regular' in page.locator('#elementFontChoice').inner_text()
            page.locator('[data-field=home_name]').click();assert 'Serif · Bold' in page.locator('#elementFontChoice').inner_text()
            navigate(page,'control');navigate(page,'editor');assert 'Serif · Bold' in page.locator('#elementFontChoice').inner_text()
            save(page);saved=request('/api/state')['layout'];assert saved['elements']['home_name']['bold'] and saved['elements']['home_name']['font']=='serif'
            assert not saved['elements']['away_name']['bold'] and saved['elements']['away_name']['font']=='heavy'
            assert saved['elements']['home_name']['transform']==saved_element['transform']
            overlay.wait_for_function("()=>document.querySelector('#overlayStage [data-id=home_name]').style.fontWeight==='800'",polling=100)
            assert style(page,'editorStage')==style(page,'previewStage')==style(overlay,'overlayStage')
            a,b=geometry(page,'editorStage'),geometry(overlay,'overlayStage')
            assert all(abs(a[k]-b[k])<.2 for k in a),(a,b)
            choose(page,'elementFont','sans');page.locator('#elementFontChoice').click();switch.click();page.keyboard.press('Escape')
            page.once('dialog',lambda d:d.accept());page.locator('#discardLayout').click()
            assert 'Serif · Bold' in page.locator('#elementFontChoice').inner_text() and request('/api/state')['layout']==saved
            page.locator('#elementFontChoice').click();page.locator('#touchChoiceDialog').screenshot(path=str(root/f'.test/font16-picker-{width}.png'));page.keyboard.press('Escape')
            no_overflow(page);assert not errors,errors;page.close();overlay.close()
            print('Font switch/family independence, scroll/focus, element drafts, Save/Discard, transformed OBS:',width,'PASS',flush=True)
        request('/api/profiles',{'name':'Font test','action':'save'})
        modified=request('/api/state')['layout'];modified['elements']['home_name'].update(font='mono',bold=False);request('/api/layout',modified,'PUT')
        request('/api/profiles',{'name':'Font test','action':'load'});saved=request('/api/state')['layout']
        assert saved['elements']['home_name']['font']=='serif' and saved['elements']['home_name']['bold']
        proc.terminate();proc.wait(timeout=5);proc=start();assert request('/api/state')['layout']==saved
        page=browser.new_page();page.goto(base);page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')");navigate(page,'editor');page.locator('[data-field=home_name]').click()
        assert 'Serif · Bold' in page.locator('#elementFontChoice').inner_text()
        print('Font preset reload, persisted layout and closed-picker label after restart PASS',flush=True)
    finally:browser.close();proc.terminate();proc.wait(timeout=5);log.close()
