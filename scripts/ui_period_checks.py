"""Period display UI and transformed editor/preview/overlay geometry checks."""
import json,os,shutil
from urllib.request import Request,urlopen
from playwright.sync_api import sync_playwright
from ui_touch_checks import navigate,no_overflow
from period_checks import label

def verify_period_ui(base,request,wait_for,fixture,root):
    def game(field,value):return request('/api/game',{'field':field,'value':value})
    original=request('/api/state')['layout']
    layout=json.loads(json.dumps(original));transform={'scale_x':1.6,'scale_y':1.3,'lock_aspect':False}
    layout['elements']['period'].update(x=900,y=400,align='center',transform=transform)
    def put(value):
        with urlopen(Request(base+'/api/layout',data=json.dumps(value).encode(),headers={'Content-Type':'application/json'},method='PUT')) as response:return json.load(response)
    put(layout)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
        try:
            for width in (375,500,1000,1440,1920):
                touch=width in (375,1000)
                request('/api/ocr/manual',{'target':'period'});game('period_overtime',False);game('period_format','number');game('period',3)
                context=browser.new_context(viewport={'width':width,'height':1080},has_touch=touch)
                page=context.new_page();page.set_default_timeout(15000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base)
                page.wait_for_function("()=>document.getElementById('periodValue').textContent==='3'")
                group=page.locator('.period-format-options');assert group.locator('[aria-checked=true]').count()==1
                assert group.locator('[tabindex="0"]').count()==1
                def select(format):
                    button=page.locator(f'[data-period-format="{format}"]')
                    assert button.is_enabled() and button.bounding_box()['height']>=72
                    if touch:button.tap()
                    else:button.click()
                    page.wait_for_function('(f)=>document.querySelector(`[data-period-format="${f}"]`).getAttribute("aria-checked")==="true"',arg=format)
                # Mouse/touch choice plus native button activation and roving keys.
                select('number');page.locator('[data-period-format=number]').focus();page.keyboard.press('ArrowRight')
                page.wait_for_function("()=>document.getElementById('periodValue').textContent==='3rd'")
                page.keyboard.press('End');page.wait_for_function("()=>document.getElementById('periodValue').textContent==='Q3'")
                page.keyboard.press('Home');page.wait_for_function("()=>document.getElementById('periodValue').textContent==='3'")
                for format in ('number','ordinal','quarter'):
                    select(format);page.once('dialog',lambda d:d.accept('11'));page.locator('#periodValue').click()
                    page.wait_for_function('(v)=>document.getElementById("periodValue").textContent===v',arg=label(11,format))
                    page.locator('[data-adjust="period:1"]').click();page.wait_for_function('(v)=>document.getElementById("periodValue").textContent===v',arg=label(12,format))
                    page.locator('[data-adjust="period:1"]').click();page.wait_for_function('(v)=>document.getElementById("periodValue").textContent===v',arg=label(13,format))
                fixture['period']=' 3rD ';wait_for(lambda s:s['ocr']['targets']['period']['recognized']==' 3rD ' and s['ocr']['targets']['period']['can_follow'])
                request('/api/ocr/follow',{'target':'period'});page.wait_for_function("()=>document.getElementById('periodValue').disabled")
                page.wait_for_function("()=>document.getElementById('ocr-period-recognized').textContent===' 3rD '")
                assert page.locator('#ocr-period-accepted').text_content()=='3'
                overlay=browser.new_page(viewport={'width':1920,'height':1080});overlay.goto(base+'/overlay');overlay.wait_for_selector('.stage-element');page.bring_to_front()
                for format in ('number','ordinal','quarter'):
                    select(format);page.wait_for_function('(v)=>document.getElementById("periodValue").textContent===v',arg=label(3,format))
                    assert request('/api/state')['ocr']['targets']['period']['following']
                    page.locator('.period-ot-control').click();page.wait_for_function("()=>document.getElementById('periodValue').textContent==='OT'")
                    fixture['period']='13th';wait_for(lambda s:s['period']==13)
                    page.locator('.period-ot-control').click();page.wait_for_function('(v)=>document.getElementById("periodValue").textContent===v',arg=label(13,format))
                    expected=label(13,format);overlay.wait_for_function('(v)=>document.querySelector("[data-id=period]").textContent===v',arg=expected,polling=100,timeout=15000)
                    navigate(page,'editor');page.locator('[data-field=period]').click()
                    assert page.locator('#freeTransform').get_attribute('aria-pressed')=='false'
                    assert page.locator('.element-resize-handle:visible').count()==0
                    def bounds(stage,tab):return tab.evaluate('s=>FieldStage.elementBox(document.getElementById(s),"period")',stage)
                    editor=bounds('editorStage',page);output=bounds('overlayStage',overlay)
                    for key in editor:assert abs(editor[key]-output[key])<.2,(key,editor,output)
                    assert page.locator('#editorStage [data-id=period]').text_content()==expected
                    assert request('/api/state')['layout']['elements']['period']['transform']==transform
                    navigate(page,'control')
                    page.wait_for_function('()=>FieldStage.elementBox(document.getElementById("previewStage"),"period")!==null')
                    preview=bounds('previewStage',page)
                    for key in editor:assert abs(editor[key]-preview[key])<.2
                    fixture['period']='3rd';wait_for(lambda s:s['period']==3)
                page.locator('[data-period-format=quarter]').focus();page.wait_for_timeout(600)
                assert page.locator('[data-period-format=quarter]').evaluate('e=>e===document.activeElement')
                fixture['period']='13rd';page.wait_for_function("()=>document.getElementById('ocr-period-warning').textContent.includes('valid ordinal')")
                assert request('/api/state')['period']==3 and page.locator('#ocr-period-accepted').text_content()=='3'
                fixture['period']='Q13';wait_for(lambda s:s['period']==13)
                no_overflow(page)
                assert page.evaluate('new Set([...document.querySelectorAll("[id]")].map(e=>e.id)).size===document.querySelectorAll("[id]").length')
                assert page.evaluate("()=>document.getElementById('tab-control').lastElementChild.matches('.ocr-card')")
                assert page.locator('.ocr-card').evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(20, 20, 20)'
                if width<=500:
                    boxes=[b.bounding_box() for b in group.locator('button').all()]
                    assert all(boxes[i+1]['y']>=boxes[i]['y']+boxes[i]['height'] for i in (0,1))
                page.locator('.period-row').scroll_into_view_if_needed();page.screenshot(path=str(root/f'.test/period13-{width}.png'))
                page.locator('.period-row').screenshot(path=str(root/f'.test/period13-controls-{width}.png'))
                assert not errors,errors
                print('Period touch/mouse/keyboard, OCR/OT, transformed editor-preview-overlay and responsive:',width,'PASS',flush=True)
                overlay.close();context.close()
        finally:browser.close();put(original)
