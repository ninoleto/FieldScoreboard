"""Real-server browser checks; all OCR readings in this suite are simulated."""
import os,shutil
from playwright.sync_api import sync_playwright
from ui_touch_checks import choose,navigate,no_overflow
TARGETS=('main','shot','home_score','away_score','home_fouls','away_fouls','period')

def verify_ocr_ui(base,request,wait_for,fixture,root,address):
    def order(page):
        assert page.evaluate('''()=>{
          const o=document.querySelector('.ocr-card'),live=document.getElementById('tab-control');
          return live.lastElementChild===o && ['.workspace','.both-clocks','.clock-grid'].every(s=>{
            const e=live.querySelector(s);return !!(e.compareDocumentPosition(o)&Node.DOCUMENT_POSITION_FOLLOWING)&&e.getBoundingClientRect().bottom<=o.getBoundingClientRect().top;
          }) && !!(o.compareDocumentPosition(document.querySelector('footer'))&Node.DOCUMENT_POSITION_FOLLOWING);
        }''')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
        try:
            for width in (375,500,1000,1440,1920):
                for target in TARGETS:request('/api/ocr/manual',{'target':target})
                context=browser.new_context(viewport={'width':width,'height':1080},has_touch=width==375)
                page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.add_init_script('''const originalFetch=window.fetch;window.fetch=async(...args)=>{
                  const response=await originalFetch(...args);
                  if(args[0]==='/api/state'&&window.__holdState){window.__holdState=false;await new Promise(resolve=>{window.__releaseState=resolve;window.__heldState=true})}
                  return response;
                };''')
                page.goto(base);page.wait_for_function("()=>document.getElementById('ocrConnection').textContent==='Connected to ScoreSight'")
                page.wait_for_timeout(600)
                assert page.evaluate('scrollY')==0,'polling scrolled page on open'
                order(page)
                page.locator('#homeName').focus();page.wait_for_timeout(600)
                assert page.locator('#homeName').evaluate('e=>e===document.activeElement') and page.evaluate('scrollY')<1080
                page.locator('#ocrAddress').fill('http://127.0.0.1:')
                navigate(page,'editor');navigate(page,'control');page.wait_for_timeout(600)
                assert page.locator('#ocrAddress').input_value()=='http://127.0.0.1:'
                assert page.locator('#ocr-main-follow').is_disabled()
                page.locator('#ocrAddress').fill(address);page.locator('#ocrConnect').click()
                page.wait_for_function("()=>!document.getElementById('ocr-main-follow').disabled")
                fixture['extra']=True
                page.wait_for_function("()=>[...document.getElementById('ocr-main-field').options].some(o=>o.value==='Alternate')")
                for target in TARGETS:
                    id=f'ocr-{target}-field'
                    assert page.locator('#'+id).is_hidden() and page.locator('#'+id).get_attribute('tabindex')=='-1'
                    page.locator('#'+id+'Choice').click();page.keyboard.press('Escape')
                    assert page.locator('#'+id+'Choice').evaluate('e=>e===document.activeElement')
                    for suffix in ('fieldChoice','follow','manual'):
                        assert page.locator(f'#ocr-{target}-{suffix}').bounding_box()['height']>=60,(width,target,suffix)
                choose(page,'ocr-main-field','Alternate')
                page.wait_for_function("()=>document.getElementById('ocr-main-recognized').textContent==='03:21'")
                choose(page,'ocr-main-field','Time')
                page.wait_for_function("()=>!document.getElementById('ocr-main-follow').disabled")
                page.locator('#ocr-main-follow').focus();page.keyboard.press('Enter')
                page.wait_for_function("()=>document.getElementById('ocr-main-mode').textContent==='FOLLOWING OCR'")
                page.locator('#ocr-home_score-follow').click()
                page.wait_for_function("()=>document.getElementById('homeScore').disabled")
                assert page.locator('[data-clock-action="both:start"]').is_disabled()
                assert page.locator('[data-clock-action="shot:start"]').is_enabled()
                assert page.locator('#awayScore').is_enabled()
                assert page.locator('#ocr-shot-fieldChoice').is_enabled()
                for target,id in [('home_fouls','homeFouls'),('away_fouls','awayFouls'),('period','periodValue')]:
                    page.locator(f'#ocr-{target}-follow').click();page.wait_for_function('(id)=>document.getElementById(id).disabled',arg=id)
                    assert page.locator(f'[data-adjust="{target}:1"]').is_disabled() and page.locator('#resetMatch').is_disabled()
                    assert page.locator('#periodOT').is_enabled(),'OT must remain an explicit manual display toggle'
                    page.locator(f'#ocr-{target}-manual').click();page.wait_for_function('(id)=>!document.getElementById(id).disabled',arg=id)
                order(page);no_overflow(page)
                assert page.locator('.ocr-card').evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(20, 20, 20)'
                assert page.locator('.ocr-target').first.evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(16, 29, 45)'
                # Connection health changes must not focus or scroll to OCR.
                page.locator('#homeName').focus();page.evaluate('scrollTo(0,0)');fixture['status']=503
                page.wait_for_function("()=>document.getElementById('ocrConnection').textContent==='Connection lost / unavailable'")
                assert page.evaluate('scrollY')==0 and page.locator('#homeName').evaluate('e=>e===document.activeElement')
                order(page);fixture['status']=200
                page.wait_for_function("()=>document.getElementById('ocrConnection').textContent==='Connected to ScoreSight'")
                assert page.evaluate('scrollY')==0
                page.screenshot(path=str(root/f'.test/ocr11-live-{width}.png'),full_page=True)
                page.locator('.ocr-card').screenshot(path=str(root/f'.test/ocr11-panel-{width}.png'))
                if width==1920:
                    page.evaluate('scrollTo(0,0)');page.screenshot(path=str(root/'.test/ocr11-maximized-1920x1080.png'))
                if width==1920:
                    page.evaluate('window.__holdState=true');page.wait_for_function('()=>window.__heldState===true')
                if width==375:page.locator('#ocr-main-manual').tap()
                else:page.locator('#ocr-main-manual').focus();page.keyboard.press('Space')
                page.wait_for_function("()=>document.getElementById('mainState').textContent==='PAUSED'")
                assert page.locator('#ocr-home_score-mode').text_content()=='FOLLOWING OCR'
                if width==1920:
                    page.evaluate('window.__releaseState()');page.wait_for_timeout(70)
                    assert page.locator('#mainState').text_content()=='PAUSED','old browser poll repainted OCR ownership'
                page.locator('#ocr-home_score-manual').click()
                page.wait_for_function("()=>!document.getElementById('homeScore').disabled")
                assert page.evaluate('new Set([...document.querySelectorAll("[id]")].map(e=>e.id)).size===document.querySelectorAll("[id]").length')
                assert not errors,errors
                print('OCR bottom order, independent cards, dialogs, drafts, touch/keyboard, polling focus/scroll:',width,'PASS',flush=True)
                context.close()
            for zoom in (2,4):
                context=browser.new_context(viewport={'width':1920//zoom,'height':1080//zoom},device_scale_factor=zoom)
                page=context.new_page();page.goto(base);page.wait_for_function("()=>document.getElementById('ocrConnection').textContent==='Connected to ScoreSight'")
                order(page);no_overflow(page)
                page.locator('#ocr-main-fieldChoice').click();no_overflow(page)
                page.screenshot(path=str(root/f'.test/ocr11-zoom-{zoom*100}.png'));page.keyboard.press('Escape')
                assert page.locator('#ocr-main-fieldChoice').evaluate('e=>e===document.activeElement')
                print('OCR zoom equivalent',zoom*100,'PASS',flush=True);context.close()
        finally:browser.close()

def verify_disconnected_ui(base):
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
        try:
            for width in (375,500,1000,1440,1920):
                page=browser.new_page(viewport={'width':width,'height':1080});page.goto(base)
                page.wait_for_function("()=>document.getElementById('connectionLabel').textContent==='Connected'")
                assert page.locator('#ocrConnection').text_content()=='Not connected'
                assert page.evaluate("()=>document.getElementById('tab-control').lastElementChild.matches('.ocr-card')&&scrollY===0")
                no_overflow(page);page.close()
            print('Disconnected restart: OCR remains last at all five widths; no opening scroll PASS',flush=True)
        finally:browser.close()
