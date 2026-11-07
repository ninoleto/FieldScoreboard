"""Real-server background regression, with an isolated config and generated art.

Usage: python scripts/test_background_ui.py /path/to/native/fieldscoreboard
Requires Playwright and Pillow for test fixtures/pixel inspection only.
"""
from pathlib import Path
from io import BytesIO
import hashlib,json,math,os,shutil,socket,subprocess,sys,tempfile,time
import urllib.request
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
from ui_touch_checks import choose,navigate,no_overflow

root=Path(__file__).resolve().parents[1]
(root/'.test').mkdir(exist_ok=True)
binary=Path(sys.argv[1]).resolve()
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'

def request(path,method='GET',body=None):
    data=None if body is None else json.dumps(body).encode()
    with urllib.request.urlopen(urllib.request.Request(base+path,data=data,method=method,headers={'Content-Type':'application/json'}),timeout=5) as r:return json.load(r)

def fixture(w,h,ext):
    img=Image.new('RGBA',(w,h),(0,0,0,0))
    draw=ImageDraw.Draw(img);draw.rectangle((w//8,h//8,w*7//8,h*7//8),fill=(32,160,100,255))
    draw.rectangle((w//3,h//3,w*2//3,h*2//3),fill=(220,80,40,128))
    data=BytesIO()
    if ext=='jpg':img=img.convert('RGB')
    img.save(data,format={'png':'PNG','jpg':'JPEG','webp':'WEBP'}[ext])
    return {'name':f'generated-{w}x{h}.{ext}','mimeType':{'png':'image/png','jpg':'image/jpeg','webp':'image/webp'}[ext],'buffer':data.getvalue()}

def rect(page,stage='editorStage'):
    return page.locator('#'+stage+' .stage-bg').evaluate('e=>({x:parseFloat(e.style.left),y:parseFloat(e.style.top),width:parseFloat(e.style.width),height:parseFloat(e.style.height)})')

def close_rect(actual,expected,tolerance=.05):
    for key in ['x','y','width','height']:assert abs(actual[key]-expected[key])<tolerance,(key,actual,expected)

def expected(mode,w,h):
    factor=min(1920/w,1080/h) if mode=='fit' else max(1920/w,1080/h) if mode=='fill' else 1
    width,height=(1920,1080) if mode=='stretch' else (w*factor,h*factor)
    return {'width':width,'height':height,'x':(1920-width)/2,'y':(1080-height)/2}

def save(page):
    page.locator('#saveLayout').click()
    page.wait_for_function("()=>!document.getElementById('saveLayout').disabled && document.getElementById('unsavedBadge').classList.contains('hidden')")

def set_number(page,id,value):
    page.locator('#'+id).fill(str(value));page.locator('#'+id).blur()

def wait_state(page):
    page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')")

with tempfile.TemporaryDirectory() as folder,sync_playwright() as p:
    config=Path(folder)/'config.json';log=(Path(folder)/'server.log').open('wb')
    def start():
        proc=subprocess.Popen([str(binary),'--config',str(config),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log)
        for _ in range(100):
            try:request('/api/state');return proc
            except OSError:time.sleep(.1)
        raise RuntimeError('Test server startup failed')
    proc=start()
    executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
    browser=p.chromium.launch(headless=True,executable_path=executable)
    try:
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base);wait_state(page);navigate(page,'editor')
        overlay=browser.new_page(viewport={'width':1920,'height':1080});overlay.goto(base+'/overlay')
        originals=request('/api/state')['layout']['elements']
        for w,h in [(400,400),(400,800),(1600,200),(1920,1080)]:
            for ext in ['png','jpg','webp']:
                art=fixture(w,h,ext);old=request('/api/state')['layout']
                page.locator('#backgroundFile').set_input_files(art)
                page.wait_for_function('(size)=>document.getElementById("backgroundOriginal").textContent===`Original: ${size[0]} × ${size[1]} px`',arg=[w,h])
                page.wait_for_function("()=>!document.getElementById('importBackground').disabled")
                assert request('/api/state')['layout']==old,'draft import went live'
                assert page.locator('#backgroundLock').is_checked()
                assert page.locator('#backgroundSizing').input_value()=='fit'
                close_rect(rect(page),expected('fit',w,h))
                for mode in ['fill','original','stretch','fit']:
                    choose(page,'backgroundSizing',mode);close_rect(rect(page),expected(mode,w,h))
                save(page)
                layout=request('/api/state')['layout'];transform=layout['background_transform']
                assert transform['original_width']==w and transform['original_height']==h
                with urllib.request.urlopen(base+'/background/'+layout['background']) as response:assert response.read()==art['buffer'],'image file modified'
                assert hashlib.sha256(art['buffer']).hexdigest() in layout['background']
                page.wait_for_function('(t)=>parseFloat(document.querySelector("#previewStage .stage-bg").style.width)===t.width',arg=transform)
                overlay.wait_for_function('(ref)=>document.querySelector(".stage-bg").dataset.path.endsWith(ref)',arg=layout['background'])
                close_rect(rect(page,'previewStage'),transform);close_rect(rect(overlay,'overlayStage'),transform)
                assert overlay.locator('.background-resize-handle,.background-selection-border').count()==0
                if w==400 and h==400 and ext=='png':
                    overlay.locator('.stage-bg').evaluate('e=>e.decode()')
                    screenshot=Image.open(BytesIO(overlay.screenshot(omit_background=True)))
                    assert screenshot.getpixel((100,700))[3]==0,'uncovered OBS canvas opaque'
                    assert screenshot.getpixel((960,540))[3] in range(125,132),'PNG alpha lost'
                    overlay.screenshot(path=str(root/'.test/background-transparent-overlay.png'),omit_background=True)
                    # A taller output viewport exposes overflow beyond the logical
                    # canvas: Fill must clip there, leaving letterboxes transparent.
                    choose(page,'backgroundSizing','fill');save(page)
                    overlay.wait_for_function('()=>parseFloat(document.querySelector(".stage-bg").style.height)===1920')
                    overlay.set_viewport_size({'width':1920,'height':1400});overlay.wait_for_timeout(100)
                    clipped=Image.open(BytesIO(overlay.screenshot(omit_background=True)))
                    assert clipped.getpixel((960,100))[3]==0 and clipped.getpixel((960,1300))[3]==0,'Fill escaped the logical canvas'
                    overlay.set_viewport_size({'width':1920,'height':1080});choose(page,'backgroundSizing','fit');save(page)
                print('Import/defaults/modes/original bytes/editor-preview-overlay:',w,h,ext,'PASS',flush=True)

        # Dedicated square fixture for predictable resize and drag geometry.
        art=fixture(400,400,'png');page.locator('#backgroundFile').set_input_files(art)
        page.wait_for_function("()=>document.getElementById('backgroundOriginal').textContent==='Original: 400 × 400 px' && !document.getElementById('importBackground').disabled")
        choose(page,'backgroundSizing','original');save(page)
        set_number(page,'backgroundWidth',800)
        assert page.locator('#backgroundHeight').input_value()=='800'
        assert page.locator('#backgroundSizing').input_value()=='custom'
        set_number(page,'backgroundHeight',500)
        assert page.locator('#backgroundWidth').input_value()=='500'
        page.locator('.background-lock').click();set_number(page,'backgroundWidth',700)
        assert page.locator('#backgroundHeight').input_value()=='500'
        set_number(page,'backgroundX',-60);set_number(page,'backgroundY',125)
        close_rect(rect(page),{'x':-60,'y':125,'width':700,'height':500})
        page.locator('#centerBackground').click();close_rect(rect(page),{'x':610,'y':290,'width':700,'height':500})
        page.locator('#fitBackground').click();assert page.locator('#backgroundLock').is_checked()
        close_rect(rect(page),expected('fit',400,400))
        # Polling and navigation must retain unfinished numeric edits.
        page.locator('#backgroundWidth').fill('');navigate(page,'control');page.wait_for_timeout(650);navigate(page,'editor')
        assert page.locator('#backgroundWidth').input_value()==''
        previous=request('/api/state')['layout'];page.locator('#saveLayout').click()
        assert request('/api/state')['layout']==previous
        page.once('dialog',lambda d:d.accept());page.locator('#discardLayout').click()
        close_rect(rect(page),previous['background_transform'])
        choose(page,'backgroundSizing','original');page.locator('#selectBackground').click()
        assert page.locator('.background-resize-handle:visible').count()==4
        assert page.locator('.background-resize-handle').first.bounding_box()['width']==56
        before=rect(page);surface=page.locator('.background-drag-surface').bounding_box()
        scale=page.locator('#editorStage').bounding_box()['width']/1920
        page.mouse.move(surface['x']+surface['width']/2,surface['y']+surface['height']/2);page.mouse.down();page.mouse.move(surface['x']+surface['width']/2+45,surface['y']+surface['height']/2+30,steps=5);page.mouse.up()
        after=rect(page);assert abs(after['x']-before['x']-45/scale)<.1;assert abs(after['y']-before['y']-30/scale)<.1
        before=after;handle=page.locator('[data-corner="se"]').bounding_box()
        page.mouse.move(handle['x']+28,handle['y']+28);page.mouse.down();page.mouse.move(handle['x']+68,handle['y']+48,steps=5);page.mouse.up()
        after=rect(page);assert abs(after['width']/after['height']-1)<.0001;assert after['width']>before['width']
        close_rect({'x':after['x'],'y':after['y'],'width':before['width'],'height':before['height']},before)
        page.locator('.background-lock').click();handle=page.locator('[data-corner="se"]').bounding_box()
        page.mouse.move(handle['x']+28,handle['y']+28);page.mouse.down();page.mouse.move(handle['x']+68,handle['y']+28,steps=5);page.mouse.up()
        assert rect(page)['width']>rect(page)['height']+20
        save(page);assert request('/api/state')['layout']['elements']==originals,'background gesture moved scoreboard elements'
        # Every axis has usable one-pixel controls; keyboard selection/resize
        # stays isolated from the scoreboard and requires explicit selection.
        for id,key in [('backgroundWidth','width'),('backgroundHeight','height'),('backgroundX','x'),('backgroundY','y')]:
            before=rect(page)[key]
            page.locator(f'[data-background-step="{id}:1"]').click()
            assert abs(rect(page)[key]-before-1)<.002
            page.locator(f'[data-background-step="{id}:-1"]').click()
            assert abs(rect(page)[key]-before)<.002
        page.locator('.background-drag-surface').focus();before=rect(page)
        page.keyboard.press('Shift+ArrowRight');assert abs(rect(page)['x']-before['x']-10)<.01
        page.locator('[data-corner="se"]').focus();before=rect(page)
        page.keyboard.press('ArrowRight');assert abs(rect(page)['width']-before['width']-1)<.01
        page.keyboard.press('Escape');assert page.locator('.background-resize-handle:visible').count()==0
        save(page)
        saved=request('/api/state')['layout']
        page.once('dialog',lambda d:d.accept());page.locator('#removeBackground').click()
        assert request('/api/state')['layout']==saved
        assert page.locator('#editorStage .stage-bg').is_hidden()
        page.once('dialog',lambda d:d.accept());page.locator('#discardLayout').click()
        close_rect(rect(page),saved['background_transform'])
        page.locator('#backgroundFile').set_input_files(fixture(400,800,'jpg'))
        page.wait_for_function("()=>document.getElementById('backgroundOriginal').textContent==='Original: 400 × 800 px' && !document.getElementById('importBackground').disabled")
        page.once('dialog',lambda d:d.accept());page.locator('#discardLayout').click()
        close_rect(rect(page),saved['background_transform'])
        assert request('/api/state')['layout']==saved
        page.locator('#profileName').fill('Background placement');page.locator('#saveProfile').click()
        page.wait_for_function("()=>document.getElementById('profileSelect').value==='Background placement'")
        stored=request('/api/state')['layout']['background_transform']
        page.locator('#fitBackground').click();save(page);choose(page,'profileSelect','Background placement');page.locator('#loadProfile').click()
        page.wait_for_function('(x)=>parseFloat(document.getElementById("backgroundX").value)===Math.round(x*1000)/1000',arg=stored['x'])
        close_rect(rect(page),stored)
        # New edits while a layout PUT is in flight survive its response.
        set_number(page,'backgroundWidth',650)
        def slow_save(route):
            if route.request.method=='PUT':time.sleep(.3)
            route.continue_()
        page.route('**/api/layout',slow_save)
        page.evaluate('''()=>{document.getElementById('saveLayout').click();setTimeout(()=>{const e=document.getElementById('backgroundWidth');e.value='750';e.dispatchEvent(new Event('input',{bubbles:true}))},50)}''')
        page.wait_for_function("()=>!document.getElementById('saveLayout').disabled && document.getElementById('backgroundWidth').value==='750'")
        assert page.locator('#unsavedBadge').is_visible()
        assert request('/api/state')['layout']['background_transform']['width']==650
        page.unroute('**/api/layout',slow_save);save(page)
        # Existing legacy layouts remain stretched until explicitly edited.
        legacy=request('/api/state')['layout'];legacy.pop('background_transform')
        request('/api/layout','PUT',legacy);page.reload();wait_state(page);navigate(page,'editor')
        page.wait_for_function("()=>document.getElementById('backgroundSizing').value==='stretch'")
        close_rect(rect(page),{'x':0,'y':0,'width':1920,'height':1080})
        assert 'background_transform' not in request('/api/state')['layout']
        page.locator('#saveLayout').click();page.wait_for_timeout(350)
        assert 'background_transform' not in request('/api/state')['layout']
        set_number(page,'backgroundWidth',900);assert page.locator('#backgroundHeight').input_value()=='900'
        save(page)
        # Responsive and keyboard/mouse access to the new twelfth choice dialog.
        final=request('/api/state')['layout']['background_transform']
        for width in [375,500,1000,1440,1920]:
            page.set_viewport_size({'width':width,'height':1000});page.wait_for_timeout(100)
            no_overflow(page);close_rect(rect(page),final)
            assert request('/api/state')['layout']['background_transform']==final
            for id in ['backgroundWidth','backgroundHeight','backgroundX','backgroundY']:assert page.locator('#'+id).bounding_box()['height']==64
            page.locator('#backgroundSizingChoice').click();page.keyboard.press('End')
            assert page.locator('#touchChoiceList [aria-selected="true"]').inner_text()=='Custom'
            assert page.locator('#touchChoiceList [role="option"]:focus').inner_text()=='Stretch to canvas'
            for row in page.locator('#touchChoiceList [role="option"]').all():
                assert row.bounding_box()['height']>=56
                assert row.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')>=18
            assert page.locator('#backgroundSizing').evaluate('e=>e.tabIndex===-1 && getComputedStyle(e).display==="none"')
            assert page.locator('select').count()==19  # Includes the ScoreSight field dialog.
            assert page.evaluate('()=>{const ids=[...document.querySelectorAll("[id]")].map(e=>e.id);return new Set(ids).size===ids.length}')
            page.keyboard.press('Escape');assert page.locator('#backgroundSizingChoice').evaluate('e=>e===document.activeElement')
            page.screenshot(path=str(root/f'.test/background-editor-{width}px.png'),full_page=True)
        # Real browser touch events move the selected graphic, not the score.
        touch=browser.new_page(viewport={'width':1000,'height':900},has_touch=True);touch.goto(base);wait_state(touch);navigate(touch,'editor')
        touch.locator('#selectBackground').tap();surface=touch.locator('.background-drag-surface');surface.scroll_into_view_if_needed();b=surface.bounding_box()
        x=b['x']+b['width']/2;y=b['y']+b['height']/2;before=rect(touch);scale=touch.locator('#editorStage').bounding_box()['width']/1920
        cdp=touch.context.new_cdp_session(touch);cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
        for i in range(1,6):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+10*i,'y':y+4*i}]});touch.wait_for_timeout(25)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
        assert abs(rect(touch)['x']-before['x']-50/scale)<.3
        assert request('/api/state')['layout']['elements']==originals
        touch.wait_for_timeout(300)
        image_box=touch.locator('#editorStage .stage-bg').bounding_box()
        border_box=touch.locator('.background-selection-border').bounding_box()
        print('Selected graphic bounds:',image_box,'selection:',border_box,flush=True)
        for key in ['x','y','width','height']:assert abs(image_box[key]-border_box[key])<2,(key,image_box,border_box)
        touch.screenshot(path=str(root/'.test/background-touch-selection.png'),full_page=True);touch.close()
        for zoom in [2,4]:
            with tempfile.TemporaryDirectory(dir=root/'.test') as zoom_folder:
                profile=Path(zoom_folder)/'Default';profile.mkdir()
                (profile/'Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(zoom)/math.log(1.2)}}}),encoding='utf-8')
                context=p.chromium.launch_persistent_context(zoom_folder,headless=True,executable_path=executable,viewport={'width':1920,'height':1080})
                zoom_page=context.pages[0];zoom_page.goto(base);wait_state(zoom_page);navigate(zoom_page,'editor')
                assert zoom_page.evaluate('innerWidth')==1920/zoom
                no_overflow(zoom_page);close_rect(rect(zoom_page),final)
                zoom_page.locator('#backgroundSizingChoice').click()
                assert zoom_page.locator('#touchChoiceDialog').evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}')
                zoom_page.evaluate('scrollTo(0,0)');zoom_page.screenshot(path=str(root/f'.test/background-zoom-{zoom*100}.png'))
                zoom_page.keyboard.press('Escape');assert zoom_page.locator('#backgroundSizingChoice').evaluate('e=>e===document.activeElement')
                assert request('/api/state')['layout']['background_transform']==final
                context.close()
        # Restart reads the exact saved transform and keeps clocks Ready.
        final=request('/api/state')['layout']['background_transform'];proc.terminate();proc.wait(timeout=5);proc=start()
        restored=request('/api/state');assert restored['layout']['background_transform']==final
        assert restored['main']['state']=='ready' and restored['shot']['state']=='ready'
        assert not errors,errors
        print('Background controls, mouse/touch gestures, clipping/alpha, drafts, Save/Discard, presets, legacy, restart, all five widths: PASS',flush=True)
    finally:
        browser.close();proc.terminate();proc.wait(timeout=5);log.close()
