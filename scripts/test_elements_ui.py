"""Native editor/OBS element-transform regression with generated state and artwork."""
from pathlib import Path
import argparse,io,json,math,os,shutil,socket,subprocess,tempfile,time
from urllib.request import Request,urlopen
from PIL import Image
from playwright.sync_api import sync_playwright
from ui_touch_checks import choose,navigate,no_overflow

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('binary');args=parser.parse_args()
root=Path(__file__).resolve().parents[1];binary=Path(args.binary).resolve();(root/'.test').mkdir(exist_ok=True)
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
def request(path,body=None,method=None):
    with urlopen(Request(base+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Content-Type':'application/json'}),timeout=4) as response:return json.load(response)
def number(page,id,value):page.locator('#'+id).fill(str(value));page.locator('#'+id).blur()
def saved(page):
    page.locator('#saveLayout').click();page.wait_for_function("()=>document.getElementById('unsavedBadge').classList.contains('hidden')&&!document.getElementById('saveLayout').disabled")
def box(page,id,stage='editorStage'):
    return page.evaluate('''([stage,id])=>FieldStage.elementBox(document.getElementById(stage),id)''',[stage,id])
def same(a,b,tolerance=.15):
    for k in ('left','top','width','height'):assert abs(a[k]-b[k])<tolerance,(k,a,b)

def mode(page,enabled,touch=False):
    button=page.locator('#freeTransform')
    if (button.get_attribute('aria-pressed')=='true')!=enabled:
        if touch:button.tap()
        else:button.click()
    assert button.text_content()==('Done transforming' if enabled else 'Free transform')
    assert button.get_attribute('aria-pressed')==str(enabled).lower()
    assert button.bounding_box()['height']>=64
    if not enabled:
        assert page.locator('.element-resize-handle:visible,.element-handle-guide:visible,.element-selection-border:visible').count()==0
        assert page.locator('.element-resize-handle').evaluate_all("nodes=>nodes.every(n=>getComputedStyle(n).display==='none'&&n.getClientRects().length===0)")

def normal(page):
    assert page.locator('#freeTransform').get_attribute('aria-pressed')=='false'
    mode(page,False)
def drag(page,locator,dx,dy,touch=False):
    page.locator('#editorFrame').scroll_into_view_if_needed();r=locator.bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2
    if touch:
        cdp=page.context.new_cdp_session(page)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
        for step in range(1,9):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+dx*step/8,'y':y+dy*step/8}]})
        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});cdp.detach()
    else:
        page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+dx,y+dy,steps=8);page.mouse.up()
    page.wait_for_timeout(80)

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
        page=browser.new_page(viewport={'width':1920,'height':1080});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base)
        page.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')");navigate(page,'editor')
        overlay=browser.new_page(viewport={'width':1920,'height':1080});overlay.goto(base+'/overlay');overlay.wait_for_selector('.stage-element')
        legacy=request('/api/state')['layout'];ids=list(legacy['elements'])
        assert all('transform' not in el for el in legacy['elements'].values())
        normal(page)
        # Mode switches are presentation-only: no save, dirty flag or geometry change.
        original=box(page,'main_clock');mode(page,True);page.wait_for_timeout(600);mode(page,False)
        same(original,box(page,'main_clock'));assert request('/api/state')['layout']==legacy
        assert page.locator('#unsavedBadge').is_hidden()
        for id in ids:
            original=box(page,id);same(original,box(overlay,id,'overlayStage'))
            page.locator(f'[data-field="{id}"]').click()
            assert page.locator('#editorSelectionLabel').text_content().startswith('Editing: ')
            normal(page)
            assert page.locator('#unsavedBadge').is_hidden(),'selecting element changed legacy layout'
            number(page,'elementX',600);number(page,'elementY',400)
            before=box(page,id);ratio=page.locator('#editorStage').bounding_box()['width']/1920
            drag(page,page.locator(f'#editorStage [data-id="{id}"]'),40*ratio,25*ratio)
            after=box(page,id);assert abs(after['left']-before['left']-40)<1.1 and abs(after['top']-before['top']-25)<1.1,(id,before,after)
            normal(page);mode(page,True)
            assert page.locator('.element-resize-handle:visible').count()==4
            drag(page,page.locator('.element-resize-handle[data-edge="se"]'),30,20)
            resized=box(page,id);assert resized['width']>after['width'] and abs(resized['width']/after['width']-resized['height']/after['height'])<.001
            # Side handles visibly stretch content only while unlocked.
            page.locator('#elementAspect').focus();page.keyboard.press('Space');assert page.locator('.element-resize-handle:visible').count()==8
            before=box(page,id);drag(page,page.locator('.element-resize-handle[data-edge="e"]'),25,0);after=box(page,id)
            assert after['width']>before['width'] and abs(after['height']-before['height'])<.1
            for alignment,fraction in [('center',.5),('right',1),('left',0)]:
                choose(page,'elementAlign',alignment);b=box(page,id)
                assert abs(b['left']+b['width']*fraction-float(page.locator('#elementX').input_value()))<.1,(id,alignment,b)
            page.locator('#elementAspect').focus();page.keyboard.press('Space');number(page,'elementWidth',180)
            assert abs(box(page,id)['width']-180)<.05
            draft=box(page,id);mode(page,False);same(draft,box(page,id))
            assert page.locator('#unsavedBadge').is_visible()
            saved(page);overlay.wait_for_timeout(250);same(box(page,id),box(overlay,id,'overlayStage'))
            # Reset drops optional properties and recreates legacy dimensions.
            page.locator('#resetElementSize').click();number(page,'elementX',legacy['elements'][id]['x']);number(page,'elementY',legacy['elements'][id]['y'])
            same(box(page,id),original);saved(page)
            print('Element move/corner/side/lock/anchor/reset + OBS geometry:',id,'PASS',flush=True)
        page.locator('[data-field="home_score"]').click();number(page,'elementX',600);number(page,'elementY',400);number(page,'elementWidth',140);saved(page)
        transform=request('/api/state')['layout']['elements']['home_score']['transform']
        request('/api/game',{'field':'home_score','value':9});page.wait_for_function("()=>document.querySelector('#editorStage [data-id=home_score]').textContent==='9'");single=box(page,'home_score')
        request('/api/game',{'field':'home_score','value':10});page.wait_for_function("()=>document.querySelector('#editorStage [data-id=home_score]').textContent==='10'");double=box(page,'home_score')
        assert double['width']>single['width']*1.8 and abs(single['height']-double['height'])<.1
        assert request('/api/state')['layout']['elements']['home_score']['transform']==transform
        page.locator('[data-field="home_name"]').click();number(page,'elementWidth',200);saved(page)
        t=request('/api/state')['layout']['elements']['home_name']['transform'];request('/api/game',{'field':'home_name','value':'LONG TEAM '+('9'*22)})
        page.wait_for_function("()=>document.querySelector('#editorStage [data-id=home_name]').textContent.startsWith('LONG')")
        assert request('/api/state')['layout']['elements']['home_name']['transform']==t
        assert page.locator('#editorStage [data-id=home_name]').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
        choose(page,'elementFont','mono');number(page,'elementSize',44);page.locator('#elementBold').uncheck();page.locator('#elementColor').fill('#ffcc88');page.locator('#elementColor').dispatch_event('change');saved(page);overlay.wait_for_timeout(250)
        assert request('/api/state')['layout']['elements']['home_name']['transform']==t
        same(box(page,'home_name'),box(overlay,'home_name','overlayStage'))
        page.locator('[data-field="home_fouls"]').click();number(page,'elementX',500);number(page,'elementY',600)
        dots=page.locator('#editorStage [data-id=home_fouls] .foul-dot').first;before=dots.bounding_box();number(page,'elementWidth',float(page.locator('#elementWidth').input_value())*2);after=dots.bounding_box()
        assert abs(after['width']/before['width']-2)<.01 and abs(after['height']/before['height']-2)<.01
        saved(page);t=request('/api/state')['layout']['elements']['home_fouls']['transform']
        request('/api/game',{'field':'home_fouls','value':30});page.wait_for_function("()=>document.querySelector('#editorStage [data-id=home_fouls]').textContent.includes('+25')")
        assert request('/api/state')['layout']['elements']['home_fouls']['transform']==t
        choose(page,'homeFoulStyle','number');saved(page);overlay.wait_for_timeout(250);assert page.locator('#editorStage [data-id=home_fouls]').text_content()=='30';same(box(page,'home_fouls'),box(overlay,'home_fouls','overlayStage'))
        # Drafts survive polling/navigation; invalid drafts block Save; Discard restores.
        original=request('/api/state')['layout'];page.locator('#elementWidth').fill('');page.wait_for_timeout(600);assert page.locator('#elementWidth').input_value()==''
        mode(page,True);mode(page,False);assert page.locator('#elementWidth').input_value()==''
        mode(page,True);navigate(page,'control');navigate(page,'editor');normal(page);assert page.locator('#elementWidth').input_value()==''
        page.locator('#saveLayout').click();assert request('/api/state')['layout']==original
        mode(page,True);page.once('dialog',lambda d:d.accept());page.locator('#discardLayout').click();same(box(page,'home_fouls'),box(overlay,'home_fouls','overlayStage'))
        assert page.locator('#unsavedBadge').is_hidden();mode(page,False)
        # Presets include transforms but do not restore game values.
        request('/api/profiles',{'name':'Element transforms','action':'save'});number(page,'elementWidth',180);mode(page,True);saved(page)
        assert page.locator('#freeTransform').get_attribute('aria-pressed')=='true';mode(page,False)
        request('/api/profiles',{'name':'Element transforms','action':'load'});page.wait_for_timeout(400)
        assert request('/api/state')['layout']==original and request('/api/state')['home_score']==10
        buf=io.BytesIO();Image.new('RGBA',(64,64),(0,100,70,120)).save(buf,format='PNG')
        with urlopen(Request(base+'/api/background',data=buf.getvalue(),headers={'Content-Type':'image/png'})) as response:json.load(response)
        page.wait_for_timeout(500);mode(page,True);page.locator('#selectBackground').click()
        assert page.locator('.element-resize-handle:visible').count()==0 and page.locator('.background-resize-handle:visible').count()==4
        assert page.locator('#editorSelectionLabel').text_content()=='Editing: Background graphic'
        normal(page);assert page.locator('#freeTransform').is_disabled()
        page.locator('#selectBackground').click();normal(page);assert page.locator('#freeTransform').is_enabled()
        mode(page,True);page.locator('[data-field="main_clock"]').click();normal(page)
        assert page.locator('.background-resize-handle:visible').count()==0
        # A readable test layout for screenshot and mouse/touch/zoom checks.
        request('/api/game',{'field':'home_name','value':'HOME'});visual=request('/api/state')['layout']
        for i,id in enumerate(ids):
            visual['elements'][id].update(x=120+(i%3)*600,y=160+(i//3)*300,align='left',transform={'scale_x':1.2,'scale_y':1.2,'lock_aspect':True})
        request('/api/layout',visual,'PUT');page.wait_for_timeout(500)
        for width,touch,zoom in [(375,True,1),(500,False,1),(1000,True,1),(1440,False,1),(1920,False,1),(960,False,2),(480,True,4)]:
            context=browser.new_context(viewport={'width':width,'height':1080//zoom},has_touch=touch,device_scale_factor=zoom)
            test=context.new_page();test.on('pageerror',lambda e:errors.append(str(e)));test.goto(base);test.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')");navigate(test,'editor')
            test.locator('[data-field="home_score"]').click();number(test,'elementX',800);number(test,'elementY',550)
            normal(test)
            ratio=test.locator('#editorStage').bounding_box()['width']/1920;before=box(test,'home_score');drag(test,test.locator('#editorStage [data-id=home_score]'),10,8,touch)
            after=box(test,'home_score');assert abs(after['left']-before['left']-10/ratio)<1.1 and abs(after['top']-before['top']-8/ratio)<1.1
            test.locator('#editorFrame').scroll_into_view_if_needed();test.screenshot(path=str(root/f'.test/elements12-normal-{width}-zoom{zoom}.png'))
            mode(test,True,touch)
            drag(test,test.locator('.element-resize-handle[data-edge="se"]'),15,10,touch);assert box(test,'home_score')['width']>after['width']
            for h in test.locator('.element-resize-handle:visible').all():assert h.bounding_box()['width']==56 and h.bounding_box()['height']==56
            no_overflow(test);test.locator('#editorFrame').scroll_into_view_if_needed();test.screenshot(path=str(root/f'.test/elements12-{width}-zoom{zoom}.png'))
            test.locator('#editorFrame').screenshot(path=str(root/f'.test/elements12-canvas-{width}-zoom{zoom}.png'))
            # Selecting a different rendered field exits mode; hidden handles never
            # intercept the next mouse/touch selection and position gesture.
            drag(test,test.locator('#editorStage [data-id=away_fouls]'),3,2,touch);normal(test)
            assert test.locator('#editorSelectionLabel').text_content()=='Editing: Away fouls'
            mode(test,True,touch);draft=box(test,'away_fouls');mode(test,False,touch);same(draft,box(test,'away_fouls'))
            mode(test,True,touch);navigate(test,'setup');navigate(test,'editor');normal(test);same(draft,box(test,'away_fouls'))
            saved(test);overlay.wait_for_timeout(250);editorboxes={id:box(test,id) for id in ids};navigate(test,'control')
            for id in ids:same(editorboxes[id],box(test,id,'previewStage'));same(editorboxes[id],box(overlay,id,'overlayStage'))
            navigate(test,'editor');normal(test);mode(test,True,touch);test.reload();test.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')");navigate(test,'editor');normal(test)
            for id in ids:same(editorboxes[id],box(test,id))
            assert overlay.locator('.element-resize-handle,.element-selection-border').count()==0
            assert test.evaluate("()=>document.getElementById('tab-control').lastElementChild.matches('.ocr-card')")
            print('Element mouse/touch/geometry/preview/OBS/responsive:',width,'zoom',zoom,'PASS',flush=True);context.close()
        for zoom in (2,4):
            with tempfile.TemporaryDirectory(dir=root/'.test') as profile_dir:
                profile=Path(profile_dir)/'Default';profile.mkdir();(profile/'Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(zoom)/math.log(1.2)}}}))
                context=p.chromium.launch_persistent_context(profile_dir,headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'),viewport={'width':1920,'height':1080})
                test=context.pages[0];test.goto(base);test.wait_for_function("()=>document.getElementById('connected').classList.contains('ok')");navigate(test,'editor')
                assert test.evaluate('innerWidth')==1920/zoom
                test.locator('[data-field="home_score"]').click();number(test,'elementX',800);number(test,'elementY',500)
                normal(test);mode(test,True)
                before=box(test,'home_score');drag(test,test.locator('.element-resize-handle[data-edge="nw"]'),-8,-6);after=box(test,'home_score')
                assert after['width']>before['width'] and abs(after['left']+after['width']-before['left']-before['width'])<1.1
                assert abs(after['top']+after['height']-before['top']-before['height'])<1.1
                test.locator('.element-resize-handle[data-edge="se"]').focus();test.keyboard.press('Shift+ArrowRight');assert box(test,'home_score')['width']>after['width']
                no_overflow(test);saved(test);print('Native browser zoom element resize/anchor/keyboard:',zoom*100,'PASS',flush=True);context.close()
        final=request('/api/state')['layout'];proc.terminate();proc.wait(timeout=5);proc=start();assert request('/api/state')['layout']==final
        assert not errors,errors
        print('Elements: all nine, dynamic text/dots, drafts, Save/Discard, presets, restart and editor-only decorations PASS',flush=True)
    except BaseException:
        log.flush();print((Path(folder)/'server.log').read_text(errors='replace'),flush=True);raise
    finally:browser.close();proc.terminate();proc.wait(timeout=5);log.close()
