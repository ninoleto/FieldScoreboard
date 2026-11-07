"""Offline Chromium regression: JS/UI rendering with deterministic API fixtures.

This is deliberately separate from real HTTP smoke tests because the test
container's Chromium policy blocks navigation to localhost.
"""
from pathlib import Path
import json
import os
import shutil
from ui_touch_checks import choose, navigate, verify_touch_interface
from ui_numeric_checks import verify_numeric_controls
from ui_nudge_checks import verify_fine_position
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
web=root/'internal/scoreboard/web'
(root/'.test').mkdir(exist_ok=True)
state=json.loads((root/'scripts/fixtures/ui_state.json').read_text(encoding='utf-8'))
mock_js='''
const original=JSON.parse(MOCKDATA);
window.__mock=original;
window.__posts=[];
window.__profiles=['Example Futsal'];
window.__interfaces={preferred_ip:'192.168.1.42',interfaces:[{name:'Ethernet',ip:'192.168.1.42',preferred:true},{name:'Wi-Fi',ip:'192.168.1.43',preferred:false}]};
Object.defineProperty(window,'sessionStorage',{configurable:true,value:{getItem:()=>null,setItem:()=>{}}});
window.EventSource=class {constructor() {this.readyState=0} close() {}};
window.fetch=async (url,opts={})=>{
 const path=typeof url==='string'?url:url.toString();
 const method=opts.method||'GET';
 const body=opts.body ? (typeof opts.body==='string'?JSON.parse(opts.body):opts.body) : {};
 if(method!=='GET')window.__posts.push({path,method,body});
 let result=window.__mock;
 if(path==='/api/adjust'){
  window.__mock[body.field]=Math.max(body.field==='period'?1:0,window.__mock[body.field]+body.delta);
  if(body.field==='period')window.__mock.period_label=window.__mock.period_overtime?'OT':String(window.__mock.period);
 }
 if(path==='/api/game'){
  window.__mock[body.field]=body.value;
  if(body.field==='period'||body.field==='period_overtime')window.__mock.period_label=window.__mock.period_overtime?'OT':String(window.__mock.period);
  if(body.field==='shot_auto_hide')window.__mock.shot_visible=!window.__mock.shot_auto_hide||window.__mock.shot.remaining_seconds<window.__mock.main.remaining_seconds;
 }
 if(path==='/api/network'&&method==='PUT'){
  window.__mock.listen=body.listen;
  window.__mock.restart_required=window.__mock.listen!==window.__mock.active_listen;
 }
 if(path==='/api/network-interfaces')result=window.__interfaces;
 if(path==='/api/layout')window.__mock.layout=body;
 if(path.startsWith('/api/clock/')&&method==='POST'){
   const [,,,clock,command]=path.split('/');
   if(clock==='both' && (command==='start'||command==='pause')){
     for(const c of ['main','shot'])window.__mock[c].state=command==='start'?'running':'paused';
   } else if(clock==='main'||clock==='shot'){
     const c=window.__mock[clock];
     if(command==='start')c.state='running';
     if(command==='pause')c.state='paused';
     if(command==='stop')c.state='stopped';
     if(command==='reset'){
       c.remaining_seconds=c.duration_seconds;
       c.display=String(c.duration_seconds).padStart(2,'0');
       c.state=clock==='shot'&&window.__mock.main.state==='running'?'running':'ready';
     }
     if(command==='set'){
       c.duration_seconds=body.seconds;
       c.remaining_seconds=body.seconds;
       c.direction=body.direction;
       c.display=String(body.seconds).padStart(2,'0');
       c.state=clock==='shot'&&window.__mock.main.state==='running'?'running':'ready';
     }
     if(command==='adjust'){
       c.remaining_seconds=Math.max(0,c.remaining_seconds+body.seconds);
       c.display=String(c.remaining_seconds).padStart(2,'0');
     }
   }
 }
 if(path==='/api/profiles'){
  if(method==='POST'&&body.action==='save')window.__profiles.push(body.name);
  if(method==='POST'&&body.action==='delete')window.__profiles=window.__profiles.filter(n=>n!==body.name);
  result={profiles:window.__profiles};
 }
 if(path==='/api/token')result={token:'example-local-only-token'};
 if(path==='/api/token/rotate')result={token:'new-local-token'};
 if(path==='/api/overlay-state')result=window.__mock;
 return {ok:true,status:200,json:async()=>structuredClone(result)};
};
void 0;
'''.replace('MOCKDATA',json.dumps(json.dumps(state)))

def offline_page(browser,width=1440,height=900,overlay=False,has_touch=False,page=None):
    page=page or browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,has_touch=has_touch)
    errors=[]
    page.on('pageerror', lambda err: errors.append(str(err)))
    if overlay:
        html=(web/'overlay.html').read_text(encoding='utf-8').replace('<link rel="stylesheet" href="/overlay.css">', '<style>'+(web/'overlay.css').read_text(encoding='utf-8')+'</style>')
        html=html.replace('<script src="/render.js" defer></script>','').replace('<script src="/overlay.js" defer></script>','')
    else:
        html=(web/'index.html').read_text(encoding='utf-8').replace('<link rel="stylesheet" href="/app.css">', '<style>'+(web/'app.css').read_text(encoding='utf-8')+'</style>')
        html=html.replace('<script src="/render.js" defer></script>','').replace('<script src="/app.js" defer></script>','').replace('<script src="/background.js" defer></script>','').replace('<script src="/elements.js" defer></script>','').replace('<script src="/ocr.js" defer></script>','')
    page.set_content(html)
    page.evaluate(mock_js)
    page.add_script_tag(content=(web/'render.js').read_text(encoding='utf-8'))
    if not overlay:page.add_script_tag(content=(web/'background.js').read_text(encoding='utf-8'))
    if not overlay:page.add_script_tag(content=(web/'elements.js').read_text(encoding='utf-8'))
    if not overlay:page.add_script_tag(content=(web/'ocr.js').read_text(encoding='utf-8'))
    page.add_script_tag(content=(web/('overlay.js' if overlay else 'app.js')).read_text(encoding='utf-8'))
    return page,errors

with sync_playwright() as p:
    executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
    browser=p.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
    page,errors=offline_page(browser)
    page.wait_for_function("document.getElementById('connected').classList.contains('ok')")
    page.wait_for_function("document.getElementById('adapterSelect').options[0].value==='192.168.1.42'")
    assert page.locator('#previewStage .stage-element').count()==9
    page.locator('[data-adjust="home_score:1"]').click()
    page.wait_for_function("document.getElementById('homeScore').textContent === '1'")
    page.locator('[data-clock-action="main:start"]').click()
    page.wait_for_function("document.getElementById('mainState').textContent === 'RUNNING'")
    page.locator('[data-clock-action="main:pause"]').click()
    page.wait_for_function("document.getElementById('mainState').textContent === 'PAUSED'")
    # Main and shot clocks remain independent, but a shot reset/preset follows
    # a RUNNING match clock, exactly as in the production API.
    assert page.locator('[data-clock-adjust="shot:-1"]').count()==1
    assert page.locator('[data-clock-adjust="shot:1"]').count()==1
    assert page.locator('[data-clock-adjust="main:-1"]').count()==1
    assert page.locator('[data-clock-adjust="main:1"]').count()==1
    # Input polling must not clobber a valid zero minute entry.
    page.locator('#mainMinutes').fill('0')
    page.wait_for_timeout(700)
    assert page.locator('#mainMinutes').input_value()=='0'
    page.locator('#mainSeconds').fill('23')
    page.locator('[data-step-input="mainSeconds:1"]').click()
    assert page.locator('#mainSeconds').input_value()=='24'
    page.locator('[data-step-input="mainMinutes:1"]').click()
    assert page.locator('#mainMinutes').input_value()=='1'
    page.locator('[data-step-input="mainMinutes:-1"]').click()
    page.locator('[data-clock-set="main"]').click()
    page.wait_for_function("window.__mock.main.duration_seconds===24")
    page.locator('#shotAutoHide').check()
    page.wait_for_function("window.__mock.shot_auto_hide===true")
    page.locator('label.period-ot-control').click()
    page.wait_for_function("document.getElementById('periodValue').textContent==='OT'")
    assert page.locator('[data-adjust="period:1"]').is_disabled()
    page.locator('label.period-ot-control').click()
    page.wait_for_function("document.getElementById('periodValue').textContent==='1'")
    assert page.locator('[data-adjust="period:1"]').is_enabled()
    page.locator('[data-clock-action="both:start"]').click()
    page.wait_for_function("document.getElementById('mainState').textContent==='RUNNING' && document.getElementById('shotState').textContent==='RUNNING'")
    page.locator('[data-clock-action="shot:reset"]').click()
    page.wait_for_function("document.getElementById('shotState').textContent === 'RUNNING'")
    page.locator('[data-clock-adjust="shot:-1"]').click()
    page.wait_for_function("document.getElementById('shotDisplay').textContent === '23'")
    page.locator('[data-clock-adjust="shot:1"]').click()
    page.wait_for_function("document.getElementById('shotDisplay').textContent === '24'")
    page.locator('[data-shot-preset="14"]').click()
    page.wait_for_function("document.getElementById('shotDisplay').textContent === '14' && document.getElementById('shotState').textContent === 'RUNNING'")
    page.locator('[data-clock-action="both:pause"]').click()
    page.wait_for_function("document.getElementById('mainState').textContent === 'PAUSED'")
    page.locator('[data-clock-action="shot:reset"]').click()
    page.wait_for_function("document.getElementById('shotState').textContent === 'READY'")
    page.screenshot(path=str(root/'.test/live-desktop.png'),full_page=True)
    navigate(page,'editor')
    page.wait_for_timeout(350)
    page.screenshot(path=str(root/'.test/editor-desktop.png'),full_page=True)
    page.locator('[data-field="home_score"]').click()
    page.locator('#elementX').fill('780');page.locator('#elementX').blur()
    page.locator('[data-element-step="elementX:1"]').click()
    assert page.locator('#elementX').input_value()=='781'
    page.locator('[data-nudge-size="10"]').click()
    page.locator('[data-nudge="right"]').click()
    assert page.locator('#elementX').input_value()=='791'
    page.locator('[data-nudge-size="5"]').click()
    assert page.locator('#unsavedBadge').is_visible()
    page.locator('#saveLayout').click()
    page.wait_for_function("window.__mock.layout.elements.home_score.x===791")
    page.wait_for_function("document.getElementById('unsavedBadge').classList.contains('hidden')")
    # Physical drag regression: screen-space movement must map to logical 1920px coordinates.
    node=page.locator('#editorStage [data-id="home_score"]')
    bounds=node.bounding_box()
    page.mouse.move(bounds['x']+12,bounds['y']+12)
    page.mouse.down()
    page.mouse.move(bounds['x']+55,bounds['y']+12,steps=4)
    page.mouse.up()
    drag_x=int(page.locator('#elementX').input_value())
    assert drag_x>791,drag_x
    page.keyboard.press('ArrowRight')
    assert int(page.locator('#elementX').input_value())==drag_x+1
    page.locator('#saveLayout').click()
    page.wait_for_function('(x)=>window.__mock.layout.elements.home_score.x===x',arg=drag_x+1)
    choose(page,'homeFoulStyle','number');page.locator('#saveLayout').click()
    page.wait_for_function("window.__mock.layout.foul_style_home==='number'")
    navigate(page,'setup')
    page.screenshot(path=str(root/'.test/setup-desktop.png'),full_page=True)
    assert page.locator('#overlayUrl').inner_text()=='http://127.0.0.1:8790/overlay'
    assert page.locator('#lanURL').inner_text()=='http://192.168.1.42:8790'
    page.locator('#networkLan').check()
    assert page.locator('#saveNetwork').is_enabled()
    page.locator('#saveNetwork').click()
    page.wait_for_function("window.__mock.listen==='0.0.0.0:8790'")
    assert page.locator('#networkRestart').is_visible()
    assert page.locator('#copyNetworkOverlay').is_disabled()  # requires actual listener restart
    # Simulate restart: LAN overlay becomes copyable and uses the actual adapter IP.
    page.evaluate("window.__mock.active_listen='0.0.0.0:8790';window.__mock.restart_required=false")
    page.wait_for_function("document.getElementById('networkOverlayUrl').textContent==='http://192.168.1.42:8790/overlay'")
    assert page.locator('#copyNetworkOverlay').is_enabled()
    assert page.locator('#networkOverlayUrl').inner_text()=='http://192.168.1.42:8790/overlay'
    choose(page,'builderAction','score:home:+1')
    assert page.locator('#builderBody').inner_text()=='{"field":"home_score","delta":1}'
    assert page.locator('#builderURL').inner_text()=='http://192.168.1.42:8790/api/adjust'
    choose(page,'builderAction','ot:on')
    assert page.locator('#builderBody').inner_text()=='{"field":"period_overtime","value":true}'
    choose(page,'builderAction','shot:set')
    assert page.locator('#builderDirectionLabel').is_hidden()
    page.locator('#builderMinutes').fill('0');page.locator('#builderSeconds').fill('14')
    assert page.locator('#builderBody').inner_text()=='{"seconds":14,"direction":"down"}'
    page.locator('[data-step-input="builderSeconds:1"]').click()
    assert page.locator('#builderBody').inner_text()=='{"seconds":15,"direction":"down"}'
    page.locator('#loadBuilderToken').click()
    page.wait_for_function("document.getElementById('tokenStatus').textContent==='Token loaded locally'")
    assert page.locator('#builderHeaders').inner_text().startswith('Authorization: Bearer')
    assert page.locator('#copyApiToken').count()==1
    assert page.locator('#rotateApiToken').count()==1
    page.once('dialog',lambda prompt:prompt.accept())
    page.locator('#rotateApiToken').click()
    page.wait_for_function("window.__posts.some(p=>p.path==='/api/token/rotate')")
    assert page.locator('#copyBuilderToken').count()==0
    choose(page,'builderAction','state:get')
    assert page.locator('#builderMethod').inner_text()=='GET'
    assert page.locator('#loadBuilderToken').count()==1
    assert page.locator('#localOverlayURL').count()==0
    assert page.locator('#networkOverlayUrl').count()==1
    assert page.locator('#copyNetworkOverlay').is_enabled()
    assert page.locator('.network-card #loadBuilderToken').count()==0
    # Every control must exist once; no network/token duplication.
    duplicates=page.evaluate("""() => {const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.filter((id,i)=>ids.indexOf(id)!==i)}""")
    assert not duplicates,duplicates
    for width in [1920,1440,1000,500,375]:
        page.set_viewport_size({'width':width,'height':800})
        page.wait_for_timeout(120)
        docwidth=page.evaluate('document.documentElement.scrollWidth')
        print('setup responsive',width,docwidth)
        if docwidth>width+2:
            print('OFFENDING',page.evaluate("""() => [...document.querySelectorAll('*')].filter(e => e.getBoundingClientRect().right > innerWidth+2 && e.getBoundingClientRect().width>0 && getComputedStyle(e).display!=='none').slice(0,20).map(e=>({tag:e.tagName,id:e.id,className:String(e.className).slice(0,60),right:Math.round(e.getBoundingClientRect().right),width:Math.round(e.getBoundingClientRect().width)}))"""))
        assert docwidth<=width+2,(width,docwidth)
        page.screenshot(path=str(root/f'.test/setup-{width}px.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':900})
    assert not errors, errors
    print('desktop controls: PASS')
    for width in [1920,1440,1000,500,375]:
        page.set_viewport_size({'width':width,'height':800});navigate(page,'editor');page.wait_for_timeout(150)
        docwidth=page.evaluate('document.documentElement.scrollWidth')
        print('responsive',width,docwidth)
        assert docwidth <= width+2, (width,docwidth)
        page.screenshot(path=str(root/f'.test/editor-{width}px.png'),full_page=True)
        if width==500:
            trigger=page.locator('#elementFont + button.touch-select-trigger')
            assert trigger.is_visible(), 'tablet picker not visible'
            trigger.click()
            assert page.locator('#touchChoiceDialog').is_visible()
            page.locator('#touchChoiceList .touch-choice-option',has_text='Monospace').click()
            assert page.locator('#elementFont').input_value()=='mono'
            assert page.locator('#touchChoiceDialog').is_hidden()
            page.locator('[data-field="away_name"]').click()
            assert page.locator('#elementFont').input_value()=='sans'
            assert 'Clean Sans' in page.locator('#elementFont + button.touch-select-trigger').inner_text()
            assert page.locator('#unsavedBadge').is_visible()
            # Touch target size and no native number input spinner in inspector.
            assert page.locator('[data-element-step="elementX:1"]').bounding_box()['height']>=48
            assert page.locator('#touchSelectDialog').count()==0

    page.close()
    overlay,errors=offline_page(browser,1920,1080,overlay=True)
    overlay.wait_for_function("document.querySelector('[data-id=\"home_score\"]').textContent==='0'")
    assert overlay.locator('#overlayStage .stage-element').count()==9
    overlay.evaluate("window.__mock.shot_visible=false")
    overlay.wait_for_function("getComputedStyle(document.querySelector('#overlayStage [data-id=\"shot_clock\"]')).display==='none'",timeout=5000)
    overlay.evaluate("window.__mock.period_label='OT'")
    overlay.wait_for_function("document.querySelector('#overlayStage [data-id=\"period\"]').textContent==='OT'",timeout=5000)
    assert overlay.evaluate('getComputedStyle(document.body).backgroundColor')=='rgba(0, 0, 0, 0)'
    overlay.screenshot(path=str(root/'.test/overlay-transparent.png'),omit_background=True)
    print('overlay transparent: PASS',errors)
    assert not errors,errors
    overlay.close()
    verify_touch_interface(browser,offline_page,root)
    verify_numeric_controls(browser,offline_page,root)
    verify_fine_position(browser,offline_page,root)
    browser.close()
print('UI checks PASS')
