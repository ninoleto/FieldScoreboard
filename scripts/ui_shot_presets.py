"""Shot preset order, touch sizing and immediate conditional resume checks."""
from ui_touch_checks import no_overflow

def verify_shot_presets(page,request,wait,width):
    card=page.locator('[data-clock=shot]')
    selectors=['.card-heading','.clock-reading','.clock-buttons','.clock-presets','.shot-duration-presets','.clock-setup','.clock-set']
    boxes=[card.locator(s).bounding_box() for s in selectors]
    for a,b in zip(boxes,boxes[1:]):assert a['y']+a['height']<=b['y']+1,(width,boxes)
    group=card.locator('.shot-duration-presets')
    assert group.locator('h4').inner_text()=='Duration presets'
    assert group.locator('#shotPresetsHelp').inner_text()=='Applies immediately'
    note='Reset / 14s / 24s / 30s: shot clock resumes automatically if the match clock is running.'
    assert page.locator('.clock-follow-note').count()==1 and group.locator('.clock-follow-note').inner_text()==note
    assert group.locator('.shot-presets').evaluate("e=>e.nextElementSibling.matches('.clock-follow-note')")
    assert group.locator('[data-shot-preset]').all_inner_texts()==['14s','24s','30s']
    assert group.locator('[data-shot-preset]').evaluate_all('els=>els.every(e=>e.getBoundingClientRect().height>=64&&parseFloat(getComputedStyle(e).fontSize)>=20)')
    setup=card.locator('.clock-setup')
    assert setup.locator('[data-shot-preset],.clock-follow-note').count()==0
    assert setup.locator('.clock-setup-help').inner_text()=='Duration applies with Set. Output format applies immediately.'
    assert setup.evaluate('e=>parseFloat(getComputedStyle(e).borderTopWidth)>=1')
    assert card.evaluate("e=>e.lastElementChild.matches('[data-clock-set=shot]')")
    for state in ('paused','running'):
        request('/api/clock/main/set',{'seconds':600,'direction':'down'})
        request('/api/clock/main/start',{})
        if state=='paused':request('/api/clock/main/pause',{})
        for seconds in (14,24,30):
            before=request('/api/state');button=group.locator(f'[data-shot-preset="{seconds}"]')
            with page.expect_response(lambda r:r.url.endswith('/api/clock/shot/set') and r.request.method=='POST') as event:
                if width==375:button.tap()
                elif seconds==24:button.focus();page.keyboard.press('Space')
                else:button.click()
            assert event.value.ok and event.value.request.post_data_json=={'seconds':seconds,'direction':'down'}
            after=wait(lambda s:s['shot']['duration_seconds']==seconds and s['shot']['state']==('running' if state=='running' else 'ready'))
            assert after['main']['state']==state and after['main']['duration_seconds']==600
            if state=='paused':assert after['main']==before['main'] and after['shot']['remaining_seconds']==seconds
            for key in ('home_score','away_score','home_fouls','away_fouls','period','period_overtime','period_format','layout'):assert after[key]==before[key],key
    request('/api/clock/both/pause',{});no_overflow(page)
    print('Shot preset order, immediate actions, paused/running resume, unrelated state:',width,'PASS',flush=True)
