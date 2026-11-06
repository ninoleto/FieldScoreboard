"""Behavior checks for the universal choice dialog and responsive operator UI."""
import json
import math
import os
from pathlib import Path
import shutil
import tempfile


def navigate(page, target):
    if page.locator('#navigationToggle').is_visible() and not page.locator('[data-tab="'+target+'"]').is_visible():
        page.locator('#navigationToggle').click()
    page.locator('[data-tab="'+target+'"]').click()


def choose(page, selector, value):
    index=page.locator('#'+selector).evaluate('(s,value)=>[...s.options].findIndex(o=>o.value===value)',value)
    assert index>=0,(selector,value)
    page.locator('#'+selector+'Choice').click()
    page.locator(f'#touchChoiceList [data-index="{index}"]').click()
    assert page.locator('#'+selector).input_value()==value
    assert page.locator('#touchChoiceDialog').is_hidden()


def no_overflow(page):
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    # Transformed 1920px stages intentionally extend inside clipped preview frames.
    bad=page.locator('button:visible,input:visible,fieldset:visible').evaluate_all('''els=>els.filter(e=>{
      const r=e.getBoundingClientRect();return r.left< -1||r.right>innerWidth+1||e.scrollWidth>e.clientWidth+2;
    }).map(e=>({id:e.id,text:e.textContent,width:e.clientWidth,scroll:e.scrollWidth}))''')
    assert not bad,bad


def verify_touch_interface(browser, offline_page, root):
    selectors={
        'control':['mainDirection'],
        'editor':['profileSelect','elementFont','elementAlign','homeFoulStyle','awayFoulStyle','mainFormat','shotFormat'],
        'setup':['adapterSelect','builderAction','builderDirection'],
    }
    assert sum(map(len,selectors.values()))==11
    for width in [375,500,1000,1440,1920]:
        page,errors=offline_page(browser,width,900)
        page.wait_for_function("document.getElementById('connected').classList.contains('ok')")
        for section,ids in selectors.items():
            navigate(page,section)
            if section=='setup':choose(page,'builderAction','main:set')
            for id in ids:
                trigger=page.locator('#'+id+'Choice')
                assert trigger.is_visible() and trigger.bounding_box()['height']>=56,(width,id)
                assert page.locator('#'+id).is_hidden()
                assert page.locator('#'+id).get_attribute('tabindex')=='-1'
                label=page.locator('#'+id).evaluate('s=>s.selectedOptions[0].textContent.trim()')
                assert label in trigger.inner_text() and label in trigger.get_attribute('aria-label')
                trigger.click()
                assert page.locator('#touchChoiceDialog').is_visible()
                rows=page.locator('#touchChoiceList [role="option"]')
                assert rows.count()==page.locator('#'+id+' option').count()
                assert rows.evaluate_all('els=>els.every(e=>e.offsetHeight>=56&&parseFloat(getComputedStyle(e).fontSize)>=18)')
                assert page.locator('#touchChoiceClose').bounding_box()['height']>=60
                no_overflow(page)
                page.keyboard.press('Escape')
                assert page.locator('#touchChoiceDialog').is_hidden()
                assert trigger.evaluate('e=>e===document.activeElement')
                assert trigger.get_attribute('aria-expanded')=='false'
            no_overflow(page)
            if width<=720:
                assert page.locator('#currentPage').is_visible()
                assert page.locator('[aria-current="page"]').get_attribute('data-tab')==section
                assert page.locator('#navigationToggle').get_attribute('aria-expanded')=='false'
            page.screenshot(path=str(root/f'.test/{section}-{width}px.png'),full_page=True)
        navigate(page,'control')
        # Resizing/zooming through the menu breakpoint must not strand focus
        # on a navigation control that becomes hidden.
        if width>720:
            page.locator('[data-tab="control"]').focus()
            page.set_viewport_size({'width':500,'height':900})
            page.wait_for_function("document.activeElement.id==='navigationToggle'")
            page.set_viewport_size({'width':width,'height':900})
            page.wait_for_function("document.activeElement.dataset.tab==='control'")
        # Controls remain wide, separated and ordered; combined actions occur once.
        for id in ['mainMinutes','mainSeconds','shotSeconds']:
            input=page.locator('#'+id)
            assert input.bounding_box()['height']==64
            assert input.evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')==28
            boxes=input.locator('..').locator('button,input').all()
            rects=[b.bounding_box() for b in boxes]
            assert rects[1]['x']-rects[0]['x']-rects[0]['width']>=9
            assert rects[2]['x']-rects[1]['x']-rects[1]['width']>=9
        page.locator('#mainMinutes').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
        assert page.locator('#mainMinutes').evaluate("e=>getComputedStyle(e).outlineStyle!=='none'")
        for action in ['start','pause']:
            assert page.locator(f'[data-clock-action="both:{action}"]').count()==1
            assert page.locator(f'.both-clocks [data-clock-action="both:{action}"]').bounding_box()['height']>=72
        assert page.locator('.both-clocks').bounding_box()['y']<page.locator('.clock-grid').bounding_box()['y']
        if width<=500:
            minutes=page.locator('#mainMinutes').bounding_box();seconds=page.locator('#mainSeconds').bounding_box()
            assert seconds['y']>minutes['y']+minutes['height']
            assert page.locator('#mainDirectionChoice').bounding_box()['y']>seconds['y']+seconds['height']
        # Zero, unfinished blank edits, carry/borrow, invalid duration, and navigation.
        page.locator('#mainMinutes').fill('0');page.locator('#mainSeconds').fill('59')
        page.locator('[data-step-input="mainSeconds:1"]').click()
        assert page.locator('#mainMinutes').input_value()=='1' and page.locator('#mainSeconds').input_value()=='0'
        page.locator('[data-step-input="mainSeconds:-1"]').click()
        assert page.locator('#mainMinutes').input_value()=='0' and page.locator('#mainSeconds').input_value()=='59'
        choose(page,'mainDirection','up')
        page.locator('#shotSeconds').fill('17')
        page.locator('#mainSeconds').fill('')
        navigate(page,'editor');page.locator('#elementX').fill('123');page.locator('#elementX').blur()
        layout_x=page.locator('#elementX').input_value()
        navigate(page,'setup');page.locator('#networkPort').fill('8799')
        page.wait_for_timeout(650)
        navigate(page,'control')
        assert page.locator('#mainMinutes').input_value()=='0'
        assert page.locator('#mainSeconds').input_value()==''
        assert page.locator('#shotSeconds').input_value()=='17'
        assert page.locator('#mainDirection').input_value()=='up'
        count=page.evaluate('window.__posts.length')
        page.locator('#mainSeconds').fill('0');page.locator('[data-clock-set="main"]').click()
        assert page.evaluate('window.__posts.length')==count
        page.locator('#mainSeconds').fill('20');page.locator('[data-clock-set="main"]').click()
        page.wait_for_function('window.__mock.main.duration_seconds===20')
        navigate(page,'editor')
        assert page.locator('#elementX').input_value()==layout_x
        assert page.locator('#unsavedBadge').is_visible()
        # Arrow navigation must not nudge a selected layout element.
        page.locator('#elementFontChoice').focus();page.keyboard.press('Enter')
        page.keyboard.press('End');page.keyboard.press('Home');page.keyboard.press('ArrowDown');page.keyboard.press('Enter')
        assert page.locator('#elementFont').input_value()=='mono'
        assert page.locator('#elementX').input_value()==layout_x
        assert page.locator('#elementFontChoice').evaluate('e=>e===document.activeElement')
        assert 'Monospace' in page.locator('#elementFontChoice').get_attribute('aria-label')
        page.locator('#elementFontChoice').click();page.keyboard.press('s');page.keyboard.press('Space')
        assert page.locator('#elementFont').input_value()=='serif'
        page.locator('#elementFontChoice').click()
        for _ in range(5):
            page.keyboard.press('Tab')
            assert page.evaluate("document.getElementById('touchChoiceDialog').contains(document.activeElement)")
        page.keyboard.press('Shift+Tab')
        assert page.evaluate("document.getElementById('touchChoiceDialog').contains(document.activeElement)")
        page.locator('#touchChoiceClose').click()
        assert page.locator('#elementFontChoice').evaluate('e=>e===document.activeElement')
        page.locator('#elementFontChoice').click();page.mouse.click(2,2)
        assert page.locator('#touchChoiceDialog').is_hidden()
        assert page.locator('#elementFontChoice').evaluate('e=>e===document.activeElement')
        # Dynamic profiles: save, choose, delete, update open dialog without losing focus.
        page.locator('#profileName').fill('Touch test profile');page.locator('#saveProfile').click()
        page.wait_for_function("document.getElementById('profileSelectChoice').textContent.includes('Touch test profile')")
        choose(page,'profileSelect','Example Futsal')
        page.once('dialog',lambda d:d.accept());page.locator('#deleteProfile').click()
        page.wait_for_function("!Array.from(document.getElementById('profileSelect').options).some(o=>o.value==='Example Futsal')")
        page.locator('#profileSelectChoice').click()
        page.evaluate("document.getElementById('profileSelect').add(new Option('Added while open','new'))")
        page.wait_for_function("document.getElementById('touchChoiceList').textContent.includes('Added while open')")
        page.keyboard.press('End');page.keyboard.press('Enter')
        assert page.locator('#profileSelect').input_value()=='new'
        navigate(page,'setup');assert page.locator('#networkPort').input_value()=='8799'
        page.evaluate("window.__interfaces={preferred_ip:'192.168.1.55',interfaces:[{name:'Replacement adapter with a long readable label',ip:'192.168.1.55'}]}")
        page.locator('#refreshAdapters').click()
        page.wait_for_function("document.getElementById('adapterSelectChoice').textContent.includes('192.168.1.55')")
        choose(page,'adapterSelect','192.168.1.55')
        assert 'Detected network adapter' in page.locator('#adapterSelectChoice').get_attribute('aria-label')
        assert '192.168.1.55:8799' in page.locator('#lanURL').inner_text()
        page.locator('#builderActionChoice').click()
        page.screenshot(path=str(root/f'.test/choices-{width}px.png'))
        page.keyboard.press('Escape')
        duplicates=page.evaluate("() => {const a=[...document.querySelectorAll('[id]')].map(e=>e.id);return a.filter((v,i)=>a.indexOf(v)!==i)}")
        assert not duplicates,duplicates
        assert not errors,errors
        print('All 11 selectors, layout, keyboard, drafts, dynamic options:',width,'PASS')
        page.close()

    # Chromium touch input, including a swipe followed by a deliberate tap.
    for width in [375,1000,1920]:
        page,errors=offline_page(browser,width,900,has_touch=True)
        navigate(page,'setup')
        trigger=page.locator('#builderActionChoice');trigger.tap()
        initial=page.locator('#builderAction').input_value()
        box=page.locator('#touchChoiceList').bounding_box()
        x=box['x']+box['width']/2;y=box['y']+box['height']-35
        cdp=page.context.new_cdp_session(page)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
        for step in range(1,11):
            cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':y-step*28}]})
            page.wait_for_timeout(35)
        cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
        page.wait_for_timeout(400)
        assert page.locator('#touchChoiceDialog').is_visible()
        assert page.locator('#builderAction').input_value()==initial
        assert page.locator('#touchChoiceList').evaluate('e=>e.scrollTop')>100
        page.locator('#touchChoiceClose').tap()
        trigger.tap();page.locator('#touchChoiceList [data-index="1"]').tap()
        assert page.locator('#touchChoiceDialog').is_hidden()
        assert page.locator('#builderAction').input_value()!=initial
        assert not errors,errors
        print('Emulated finger scroll and tap:',width,'PASS')
        page.close()

    verify_browser_zoom(browser,offline_page,root)


def verify_browser_zoom(browser,offline_page,root):
    # Real Chromium page zoom in isolated profiles (same zoom preference as the
    # browser menu), not CSS zoom, device scaling or a simulated pinch gesture.
    for zoom in [2,4]:
        with tempfile.TemporaryDirectory(dir=root/'.test') as folder:
            profile=Path(folder)/'Default';profile.mkdir()
            (profile/'Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(zoom)/math.log(1.2)}}}),encoding='utf-8')
            executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
            context=browser.browser_type.launch_persistent_context(folder,headless=True,executable_path=executable,viewport={'width':1920,'height':1080})
            page=context.pages[0]
            page.route('http://scoreboard.test/**',lambda r:r.fulfill(body='<html></html>',content_type='text/html'))
            page.goto('http://scoreboard.test/')
            assert page.evaluate('innerWidth')==1920/zoom
            assert abs(page.evaluate('devicePixelRatio')-zoom)<.01
            page,errors=offline_page(browser,page=page)
            for target in ['control','editor','setup']:
                navigate(page,target);no_overflow(page)
                page.evaluate('scrollTo(0,0)');page.wait_for_timeout(100)
                page.screenshot(path=str(root/f'.test/zoom-{zoom*100}-{target}.png'))
                assert page.evaluate('innerWidth')==1920/zoom
            page.locator('#builderActionChoice').click();no_overflow(page)
            assert page.locator('#touchChoiceDialog').evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight}')
            # CDP screenshot offsets at native zoom can capture outside the
            # surface when the document is scrolled. The fixed modal has already
            # been checked at that position; capture it at the scroll origin.
            page.evaluate('scrollTo(0,0)');page.wait_for_timeout(100)
            page.screenshot(path=str(root/f'.test/zoom-{zoom*100}-choices.png'))
            page.keyboard.press('End');page.keyboard.press('Enter')
            assert page.locator('#builderAction').input_value()=='state:get'
            assert not errors,errors
            context.close()
    print('Native browser zoom 200% / 400%, all pages and dialog: PASS')
