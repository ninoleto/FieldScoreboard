"""Native floating preview/draft isolation, UI typography and input regression."""
from pathlib import Path
from io import BytesIO
import base64, json, math, os, shutil, socket, subprocess, sys, tempfile, time
from urllib.request import Request, urlopen
from PIL import Image
from playwright.sync_api import sync_playwright, expect
from ui_touch_checks import choose, navigate, no_overflow

root=Path(__file__).resolve().parents[1]
output=root/'.test/ocr-format4';output.mkdir(exist_ok=True)
binary=Path(sys.argv[1]).resolve()
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
key='field_scoreboard_floating_preview_v1'
def req(path,body=None,method=None):
    data=body if isinstance(body,bytes) else json.dumps(body).encode() if body is not None else None
    with urlopen(Request(base+path,data=data,method=method,headers={'Content-Type':'application/json'}),timeout=5) as r:return json.load(r)
def bounds(page):
    return page.locator('#floatingPreview').evaluate('e=>{const r=e.getBoundingClientRect(),v=visualViewport;return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height,vw:v.width,vh:v.height}}')
def within(page):
    b=bounds(page)
    assert b['left']>=-1 and b['top']>=-1 and b['right']<=b['vw']+1 and b['bottom']<=b['vh']+1,b
    f=page.locator('#floatingFrame').bounding_box()
    assert abs(f['width']/f['height']-16/9)<.01,f
    no_overflow(page)
def scroll_away(page,tab):
    page.locator('#ocr-main-heading' if tab=='control' else '#elementColor').scroll_into_view_if_needed()
def float_visible(page):expect(page.locator('#floatingPreview')).to_be_visible();within(page)
def capture(page,name):
    session=page.context.new_cdp_session(page)
    data=base64.b64decode(session.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data'])
    with Image.open(BytesIO(data)) as im:assert any(a!=b for a,b in im.convert('RGB').getextrema())
    (output/name).write_bytes(data);session.detach()

with tempfile.TemporaryDirectory() as folder,sync_playwright() as pw:
    log=(Path(folder)/'server.log').open('wb')
    proc=subprocess.Popen([str(binary),'--config',str(Path(folder)/'config.json'),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:
        for _ in range(100):
            try:initial=req('/api/state');break
            except OSError:time.sleep(.05)
        else:raise AssertionError('Startup failed')
        image=BytesIO();Image.new('RGBA',(640,360),(30,120,70,170)).save(image,format='PNG')
        upload=req('/api/background?draft=1',image.getvalue())
        layout=initial['layout'];layout['background']=upload['background'];layout['background_transform']=upload['background_transform']
        req('/api/layout?preserve_display=1',layout,'PUT')
        browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
        context=browser.new_context(viewport={'width':1440,'height':1080})
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base);expect(page.locator('#connected')).to_have_class('connection ok')
        assert page.evaluate('getComputedStyle(document.documentElement).fontFamily')=='"Segoe UI", Arial, sans-serif'
        assert page.locator('h1').evaluate('e=>getComputedStyle(e).fontStyle')=='normal'
        assert 'Inter' not in page.locator('#previewStage [data-id="main_clock"]').evaluate('e=>getComputedStyle(e).fontFamily')
        scroll_away(page,'control');expect(page.locator('#floatingPreview')).to_be_hidden()
        assert not page.locator('#floating-control-enabled').is_checked() and not page.locator('#floating-editor-enabled').is_checked()
        page.locator('label:has(#floating-control-enabled)').click()
        page.locator('#previewStage').scroll_into_view_if_needed();expect(page.locator('#floatingPreview')).to_be_hidden()
        scroll_away(page,'control');float_visible(page)
        assert page.locator('#floatingStage .stage-element').count()==9
        expect(page.locator('#floatingStage .stage-bg')).to_be_visible()
        saved=req('/api/state')['layout']
        for field,value in [('home_score',123),('away_score',456),('home_fouls',4),('away_fouls',2),('period',3),('home_name','ALPHA'),('away_name','BETA')]:req('/api/game',{'field':field,'value':value})
        req('/api/clock/main/set',{'seconds':65,'direction':'down'});req('/api/clock/shot/set',{'seconds':14,'direction':'down'})
        for field,value in [('home_score','123'),('away_score','456'),('home_name','ALPHA'),('away_name','BETA'),('period','3'),('main_clock','01:05'),('shot_clock','14')]:expect(page.locator(f'#floatingStage [data-id="{field}"]')).to_have_text(value)
        assert page.locator('#floatingStage [data-id="home_fouls"] .filled').count()==4
        mutations=[];page.on('request',lambda r:mutations.append(r.url) if r.method not in ('GET','HEAD') else None)
        for width in (320,480,640):
            page.locator(f'[data-floating-size="{width}"]').click();within(page)
            assert abs(page.locator('#floatingFrame').bounding_box()['width']-width)<1
        page.locator('[data-floating-size="320"]').click()
        before=bounds(page);move=page.locator('#floatingMove');b=move.bounding_box()
        page.mouse.move(b['x']+30,b['y']+24);page.mouse.down();page.mouse.move(b['x']-120,b['y']-90,steps=5);page.mouse.up()
        assert bounds(page)['left']<before['left']-100;within(page)
        resize=page.locator('#floatingResize');b=resize.bounding_box();page.mouse.move(b['x']+24,b['y']+24);page.mouse.down();page.mouse.move(b['x']+104,b['y']+69,steps=5);page.mouse.up()
        assert bounds(page)['width']>350;within(page)
        move.focus();before=bounds(page);page.keyboard.press('ArrowLeft');assert abs(bounds(page)['left']-(before['left']-10))<1
        page.keyboard.press('Shift+ArrowUp');assert abs(bounds(page)['top']-(before['top']-1))<1
        resize.focus();before=bounds(page);page.keyboard.press('ArrowLeft');assert abs(bounds(page)['width']-(before['width']-10))<1
        page.locator('#floatingFrame').click(force=True)
        assert mutations==[],mutations
        stored=page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',key)
        page.reload();scroll_away(page,'control');float_visible(page)
        assert page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',key)==stored
        page.locator('#mainMinutes').focus();scroll_away(page,'control')
        page.locator('#floatingClose').click();expect(page.locator('#floatingPreview')).to_be_hidden()
        page.evaluate('scrollBy(0,100)');page.wait_for_timeout(400);expect(page.locator('#floatingPreview')).to_be_hidden()
        page.reload();scroll_away(page,'control');expect(page.locator('#floatingPreview')).to_be_hidden()
        assert not page.locator('#floating-control-enabled').is_checked()
        # Editor preview consumes the draft, and never changes saved OBS early.
        navigate(page,'editor');page.locator('label:has(#floating-editor-enabled)').click()
        page.locator('#editorFrame').scroll_into_view_if_needed();expect(page.locator('#floatingPreview')).to_be_hidden()
        page.locator('#elementX').fill('777');page.locator('#elementX').blur()
        page.locator('#elementSize').fill('120');page.locator('#elementSize').blur()
        choose(page,'elementFont','serif');choose(page,'elementAlign','right')
        page.locator('#elementColor').fill('#ff8800');page.locator('#elementColor').dispatch_event('change')
        scroll_away(page,'editor');float_visible(page)
        expect(page.locator('#floatingTitle')).to_have_text('Layout draft')
        mini=page.locator('#floatingStage [data-id="main_clock"]')
        assert mini.evaluate('e=>[e.style.left,e.style.fontSize,e.style.color,e.dataset.align]')==['777px','120px','rgb(255, 136, 0)','right']
        assert 'Georgia' in mini.evaluate('e=>e.style.fontFamily')
        assert req('/api/overlay-state')['layout']==saved
        page.locator('#elementVisible').uncheck();scroll_away(page,'editor');expect(mini).to_be_hidden()
        page.locator('#elementVisible').check()
        page.locator('#elementWidth').fill('500');page.locator('#elementWidth').blur()
        scroll_away(page,'editor');float_visible(page);assert 'scale(' in mini.get_attribute('style')
        assert req('/api/overlay-state')['layout']==saved
        # Moving/resizing the floating preview cannot reach editor key handlers.
        x=page.locator('#elementX').input_value();page.locator('#floatingMove').focus();page.keyboard.press('ArrowLeft');page.locator('#floatingResize').focus();page.keyboard.press('ArrowUp')
        assert page.locator('#elementX').input_value()==x and req('/api/overlay-state')['layout']==saved
        page.on('dialog',lambda d:d.accept())
        page.locator('#discardLayout').click();scroll_away(page,'editor');float_visible(page)
        assert mini.evaluate('e=>e.style.left')==str(saved['elements']['main_clock']['x'])+'px'
        # Background numeric drafts and element changes use the same renderer.
        page.locator('#elementX').fill('888');page.locator('#elementX').blur()
        page.locator('#backgroundX').fill('123');page.locator('#backgroundX').blur()
        scroll_away(page,'editor');float_visible(page)
        assert page.locator('#floatingStage .stage-bg').evaluate('e=>e.style.left')=='123px'
        assert req('/api/overlay-state')['layout']==saved
        page.locator('#saveLayout').click()
        page.wait_for_function('()=>document.getElementById("unsavedBadge").classList.contains("hidden")')
        assert req('/api/overlay-state')['layout']['elements']['main_clock']['x']==888
        assert req('/api/overlay-state')['layout']['background_transform']['x']==123
        navigate(page,'control');scroll_away(page,'control');expect(page.locator('#floatingPreview')).to_be_hidden()
        navigate(page,'editor');scroll_away(page,'editor');float_visible(page)
        assert page.locator('#floatingPreview').count()==1
        navigate(page,'setup');expect(page.locator('#floatingPreview')).to_be_hidden()
        assert not errors,errors
        context.close()
        req('/api/layout?preserve_display=1',saved,'PUT')
        print('Floating preview: defaults, live values, pointer/keyboard move/resize, close/reload, separate tabs, draft/OBS isolation, Save/Discard and UI fonts PASS',flush=True)
        # Responsive/clamped sizes, emulated touch and browser-local persistence.
        for width in (375,500,1000,1440,1920):
            c=browser.new_context(viewport={'width':width,'height':1080},has_touch=width==375);p=c.new_page();p.goto(base)
            p.locator('label:has(#floating-control-enabled)').click();scroll_away(p,'control');float_visible(p)
            for size in (320,480,640):p.locator(f'[data-floating-size="{size}"]').click();within(p)
            if width==375:
                client=c.new_cdp_session(p);b=p.locator('#floatingMove').bounding_box();start={'x':b['x']+45,'y':b['y']+20}
                client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[start]})
                client.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':start['x']-20,'y':start['y']-100}]})
                client.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});within(p)
                b=p.locator('#floatingResize').bounding_box();start={'x':b['x']+24,'y':b['y']+24}
                client.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[start]})
                client.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':start['x']-60,'y':start['y']-34}]})
                client.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});within(p)
            capture(p,f'floating-live-{width}.png')
            navigate(p,'editor');p.locator('label:has(#floating-editor-enabled)').click();scroll_away(p,'editor');float_visible(p)
            capture(p,f'floating-editor-{width}.png');c.close()
            print('Floating preview responsive/touch:',width,'PASS',flush=True)
        browser.close()
        for zoom in (2,4):
            with tempfile.TemporaryDirectory() as profile:
                default=Path(profile)/'Default';default.mkdir()
                (default/'Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(zoom)/math.log(1.2)}}}))
                c=pw.chromium.launch_persistent_context(profile,headless=True,viewport={'width':1920,'height':1080},executable_path=pw.chromium.executable_path)
                try:
                    p=c.pages[0];p.goto(base);assert p.evaluate('innerWidth')==1920/zoom
                    for tab in ('control','editor'):
                        navigate(p,tab);p.locator(f'label:has(#floating-{tab}-enabled)').click();scroll_away(p,tab);float_visible(p)
                        p.locator('[data-floating-size="640"]').click();within(p)
                        p.locator('#floatingResize').focus();p.keyboard.press('ArrowRight');within(p)
                        capture(p,f'floating-{tab}-zoom-{zoom*100}.png')
                finally:c.close()
            print('Floating preview real zoom:',zoom*100,'PASS',flush=True)
    finally:
        proc.terminate();proc.wait(timeout=5);log.close()
