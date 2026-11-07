"""Pending match-duration presets; uses the real server from test_clock_ui."""
from ui_touch_checks import choose,navigate

def verify_duration_presets(page,request,wait,root,width):
    buttons=page.locator('[data-main-duration]')
    assert buttons.all_inner_texts()==['5 min','8 min','10 min','12 min','20 min']
    assert page.locator('#durationPresetsHelp').inner_text()=='Choose a duration, then press Set match clock.'
    assert buttons.evaluate_all('els=>els.every(e=>e.getBoundingClientRect().height>=64&&parseFloat(getComputedStyle(e).fontSize)>=18)')
    assert page.locator('[data-clock=main]').evaluate("e=>e.lastElementChild.dataset.clockSet==='main'")
    for field,value in [('home_score',42),('away_score',39),('home_fouls',3),('away_fouls',2),('period',3),('period_overtime',True)]:request('/api/game',{'field':field,'value':value})
    writes=[]
    def record(req):
        if req.method not in ('GET','HEAD'):writes.append(req.url)
    page.on('request',record)
    for state in ('paused','running'):
        request('/api/clock/main/set',{'seconds':600,'direction':'down'})
        request('/api/clock/shot/set',{'seconds':60,'direction':'down'})
        request('/api/clock/main/start',{})
        if state=='paused':request('/api/clock/main/pause',{})
        choose(page,'mainDirection','up');choose(page,'mainFormat','M:SS')
        page.wait_for_function("()=>document.getElementById('displayStatus').textContent===''")
        before=request('/api/state');count=len(writes)
        for minutes in (5,8,10,12,20):
            button=page.locator(f'[data-main-duration="{minutes}"]')
            if width==375:button.tap()
            elif minutes==8:button.focus();page.keyboard.press('Space')
            else:button.click()
            page.wait_for_timeout(280)
            assert page.locator('#mainMinutes').input_value()==str(minutes) and page.locator('#mainSeconds').input_value()=='0'
            assert page.locator('[data-main-duration][aria-pressed=true]').get_attribute('data-main-duration')==str(minutes)
            assert page.locator('#mainDirection').input_value()=='up' and page.locator('#mainFormat').input_value()=='M:SS'
        for id,value in [('mainSeconds','1'),('mainSeconds',''),('mainMinutes','7')]:
            page.locator('#'+id).fill(value);assert page.locator('[data-main-duration][aria-pressed=true]').count()==0
        page.locator('[data-main-duration="12"]').click();navigate(page,'editor');navigate(page,'control');page.wait_for_timeout(350)
        assert page.locator('#mainMinutes').input_value()=='12' and page.locator('[data-main-duration="12"]').get_attribute('aria-pressed')=='true'
        after=request('/api/state');assert len(writes)==count,'preset/custom draft sent a live action'
        for key in ('home_score','away_score','home_fouls','away_fouls','period','period_overtime','period_format','period_label','shot','layout'):assert after[key]==before[key],key
        assert after['main']['state']==state and after['main']['duration_seconds']==600 and after['main']['direction']=='down'
        if state=='paused':assert after['main']==before['main']
        else:assert 0<after['main']['remaining_seconds']<before['main']['remaining_seconds']
        assert {k:v['following'] for k,v in after['ocr']['targets'].items()}=={k:v['following'] for k,v in before['ocr']['targets'].items()}
        page.locator('[data-clock-set=main]').click();set_state=wait(lambda s:s['main']['duration_seconds']==720 and s['main']['direction']=='up')
        assert set_state['main']['state']=='ready' and set_state['main']['remaining_seconds']==0 and set_state['shot']==before['shot']
        assert page.locator('#mainFormat').input_value()=='M:SS'
    page.locator('.match-duration-presets').screenshot(path=str(root/f'.test/presets16-{width}.png'))
    page.remove_listener('request',record)
    print('Duration presets: no live writes paused/running, direction/format, custom highlight, Set:',width,'PASS',flush=True)
