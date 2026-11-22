"""Presentation-only OCR styles; exact source values still come from Go."""
import copy

def verify_styles(request,wait_for,fixture):
    request('/api/ocr/manual',{'target':'main'})
    request('/api/display',{'field':'main_clock_format','value':'HH:MM:SS'})
    fixture.update(text='01:05',state='Success',status=200,missing=False,delay=0)
    request('/api/ocr/time-format',{'enabled':True,'final_minute_format':'SS','final_minute_style':'clean'})
    wait_for(lambda s:s['ocr']['can_follow'])
    request('/api/ocr/follow',{'target':'main'})
    cases=[]
    for style in ('visible','invisible','clean'):
        for mode in ('SS','SS.t'):
            request('/api/ocr/time-format',{'enabled':True,'final_minute_format':mode,'final_minute_style':style})
            samples=[]
            for raw,value,whole,tenth in [('01:05',65,'01:05','01:05'),('01:00',60,'01:00','01:00'),('59.9',59.9,'59','59.9'),('32.5',32.5,'32','32.5'),('5.0',5,'05','05.0'),('0.0',0,'00','00.0'),('20:00',1200,'20:00','20:00')]:
                fixture['text']=raw
                s=wait_for(lambda s:s['ocr']['last_accepted']==raw)
                expected=tenth if mode=='SS.t' else whole
                if value<60:expected={'visible':'00:','invisible':':','clean':''}[style]+expected
                assert s['main']['display']==expected and s['main']['remaining_seconds']==value,s['main']
                assert s['main']['display_style']==style and s['main'].get('display_tenths',False)==(mode=='SS.t')
                assert request('/api/overlay-state')['main']==s['main']
                samples.append(copy.deepcopy(s))
            cases.append({'style':style,'mode':mode,'samples':samples})
    fixture['text']='32.5';wait_for(lambda s:s['main']['remaining_seconds']==32.5)
    held=request('/api/ocr/manual',{'target':'main'})
    assert held['main']['display']=='00:00:33' and 'display_style' not in held['main']
    request('/api/display',{'field':'main_clock_format','value':'MM:SS'})
    request('/api/ocr/time-format',{'enabled':False,'final_minute_format':'SS','final_minute_style':'clean'})
    print('SIMULATED OCR styles: all three styles x whole/tenths, exact boundaries, zero/reset, sanitized output and manual restoration PASS',flush=True)
    return cases

def verify_style_ui(base,request,wait_for,fixture,root,cases):
    import os,shutil
    from playwright.sync_api import sync_playwright,expect
    from ui_touch_checks import choose,navigate
    matrix=r'''cases=>{
      const host=document.createElement('div');host.style.cssText='position:relative;width:1920px;height:1080px';document.body.append(host);
      const stage=document.createElement('div');stage.className='stage';host.append(stage);
      const failures=[];let checked=0;
      for(const kind of ['stage-preview','stage-editor','stage-floating']){
       stage.className='stage '+kind;
       for(const font of ['sans','mono','serif','heavy'])for(const align of ['left','center','right'])for(const size of [24,70,180])for(const transform of [null,{scale_x:1.6,scale_y:1.6,lock_aspect:true},{scale_x:.7,scale_y:1.8,lock_aspect:false}])for(const c of cases){
        let baseline=null;
        for(const s of c.samples){
         const layout=structuredClone(s.layout);Object.assign(layout.elements.main_clock,{x:960,y:80,font,align,size,bold:size!==70,transform});
         FieldStage.paint(stage,s,layout,null);
         const node=stage.querySelector('[data-id="main_clock"]');
         if(c.style==='clean'&&c.mode==='SS.t'){
          const plain=node.cloneNode(false);plain.textContent=s.main.display;stage.append(plain);
          const a=node.getBoundingClientRect(),b=plain.getBoundingClientRect(),anchor=align==='right'?1:align==='center'?.5:0;
          if(node.querySelector('.clock-run')||['left','top','width','height'].some(k=>Math.abs(a[k]-b[k])>.03))failures.push('Clean tenths differ from natural text');
          if(Math.abs(a.left+a.width*anchor-host.getBoundingClientRect().left-960)>.03)failures.push('Clean tenths anchor shifted');
          if(node.textContent!==s.main.display)failures.push('Wrong clean text');
          plain.remove();continue;
         }
         const seconds=node.querySelector('.clock-seconds'),colon=node.querySelector('.clock-colon');
         const r=node.getBoundingClientRect(),a=seconds.getBoundingClientRect(),b=colon.getBoundingClientRect();
         const geometry=[r.width,a.left,b.left,a.width];
         if(node.textContent!==s.main.display)failures.push('Wrong text');
         if(baseline&&geometry.some((v,i)=>Math.abs(v-baseline[i])>.03))failures.push(JSON.stringify({font,align,size,transform,style:c.style,mode:c.mode,value:s.main.display,baseline,geometry}));
         baseline=geometry;
        }
        checked++;
       }
      }
      host.remove();return {checked,failures:failures.slice(0,5)};
    }'''
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
        context=browser.new_context(viewport={'width':1920,'height':1080});page=context.new_page();page.goto(base)
        fixture.update(text='59.9',state='Success',status=200,missing=False,delay=0)
        request('/api/ocr/manual',{'target':'main'})
        request('/api/ocr/time-format',{'enabled':False,'final_minute_format':'SS','final_minute_style':'clean'})
        expect(page.locator('#ocr-main-auto-format')).not_to_be_checked()
        page.locator('label[for="ocr-main-auto-format"]').click()
        choose(page,'ocr-main-final-format','SS.t')
        choose(page,'ocr-main-final-style','invisible')
        expect(page.locator('#ocr-main-final-styleChoice')).to_be_focused()
        wait_for(lambda s:s['ocr']['can_follow']);page.locator('#ocr-main-follow').click()
        wait_for(lambda s:s['main']['display']==':59.9')
        expect(page.locator('#previewStage [data-id="main_clock"]')).to_have_text(':59.9')
        page.locator('label:has(#floating-control-enabled)').click()
        page.locator('#ocr-main-heading').scroll_into_view_if_needed()
        expect(page.locator('#floatingPreview')).to_be_visible()
        expect(page.locator('#floatingStage [data-id="main_clock"]')).to_have_text(':59.9')
        page.locator('#floatingMove').focus();page.keyboard.press('ArrowLeft')
        assert request('/api/state')['ocr']['following']
        overlay=context.new_page();overlay.goto(base+'/overlay')
        expect(overlay.locator('[data-id="main_clock"]')).to_have_text(':59.9')
        # Every existing manual format remains usable while decimal OCR follows.
        formats=[('MM:SS','00:49'),('M:SS','0:49'),('HH:MM:SS','00:00:49'),('SS','49'),('MM:SS.t','00:48.2')]
        assert page.locator('#mainFormat option').evaluate_all('es=>es.map(e=>e.value)')==[f for f,_ in formats]
        fixture['text']='48.2';wait_for(lambda s:s['main']['remaining_seconds']==48.2)
        for format,manual in formats:
            choose(page,'mainFormat',format)
            for enabled in (False,True):
                request('/api/ocr/time-format',{'enabled':enabled,'final_minute_format':'SS.t','final_minute_style':'clean'})
                expected='48.2' if enabled else manual
                for target,selector in [(page,'#previewStage'),(overlay,'#overlayStage')]:
                    expect(target.locator(selector+' [data-id="main_clock"]')).to_have_text(expected)
                    assert target.locator(selector+' [data-id="main_clock"] .clock-run').count()==0
                state=request('/api/state')
                assert state['main']['remaining_seconds']==48.2 and state['ocr']['following']
        choose(page,'mainFormat','MM:SS')
        request('/api/ocr/time-format',{'enabled':True,'final_minute_format':'SS.t','final_minute_style':'invisible'})
        fixture['text']='59.9';wait_for(lambda s:s['main']['display']==':59.9')
        print('All five unchanged manual output choices with decimal OCR, automatic ON/OFF and shared preview/OBS PASS',flush=True)
        navigate(page,'editor');expect(page.locator('#editorStage [data-id="main_clock"]')).to_have_text(':59.9')
        page.locator('label:has(#floating-editor-enabled)').click();page.locator('#elementColor').scroll_into_view_if_needed()
        expect(page.locator('#floatingStage [data-id="main_clock"]')).to_have_text(':59.9')
        fixture['text']='32.5';wait_for(lambda s:s['main']['display']==':32.5')
        expect(page.locator('#floatingStage [data-id="main_clock"]')).to_have_text(':32.5')
        fixture['text']='59.9';wait_for(lambda s:s['main']['display']==':59.9')
        for target,name in [(page,'operator'),(overlay,'OBS')]:
            result=target.evaluate(matrix,cases)
            assert not result['failures'],(name,result)
            print('OCR clock geometry:',name,result['checked'],'style/font/size/alignment/transform combinations PASS',flush=True)
        # Capture actual backend-driven output for every style and precision.
        # A test-only dark backing makes the transparent overlay's white text
        # readable in PNG viewers; it does not change element geometry.
        overlay.evaluate("document.body.style.setProperty('background-color','#101c2c','important')")
        assert overlay.evaluate('getComputedStyle(document.body).backgroundColor')=='rgb(16, 28, 44)'
        for c in cases:
            request('/api/ocr/time-format',{'enabled':True,'final_minute_format':c['mode'],'final_minute_style':c['style']})
            text={'visible':'00:','invisible':':','clean':''}[c['style']]+('59.9' if c['mode']=='SS.t' else '59')
            expect(overlay.locator('[data-id="main_clock"]')).to_have_text(text)
            overlay.screenshot(path=str(root/'.test/release-v0.1.3'/f'clock-{c["style"]}-{c["mode"]}.png'))
        navigate(page,'control');page.reload()
        assert page.locator('#ocr-main-final-style').input_value()=='clean'
        request('/api/ocr/manual',{'target':'main'})
        request('/api/ocr/time-format',{'enabled':False,'final_minute_format':'SS','final_minute_style':'clean'})
        context.close();browser.close()
    print('OCR style selector, focus, saved preference, live/editor/OBS output and stable columns PASS',flush=True)
