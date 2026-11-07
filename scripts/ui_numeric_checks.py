"""Focused regression for all 23 numeric +/- groups and background discovery."""
from ui_touch_checks import choose, navigate, no_overflow
import json


def verify_numeric_controls(browser, offline_page, root):
    limits={'periodValue':'20','homeScore':'999','awayScore':'999','homeFouls':'30','awayFouls':'30',
            'mainMinutes':'10079','mainSeconds':'59','shotSeconds':'3600','elementX':'1920','elementY':'1080',
            'elementWidth':'200000','elementHeight':'200000','elementSize':'240','foulDotsMax':'20','backgroundWidth':'15728640','backgroundHeight':'15728640',
            'backgroundX':'-15728640','backgroundY':'-15728640','builderMinutes':'10079','builderSeconds':'59',
            'networkPort':'65535','builderDelta':'-604800','builderPeriod':'20'}
    for width in [375,500,1000,1440,1920]:
        page,errors=offline_page(browser,width,1080)
        page.wait_for_function("document.getElementById('connected').classList.contains('ok')")
        # Metadata enables background fields; real image bytes/gestures are
        # separately covered by the real-server background regression.
        page.evaluate("""()=>{window.__mock.layout.background='numeric-check.png';
            window.__mock.layout.background_transform={mode:'fit',width:1080,height:1080,x:420,y:0,original_width:400,original_height:400,lock_aspect:true}}""")
        page.wait_for_timeout(300)
        page.evaluate("""()=>{const c=document.createElement('canvas');c.width=400;c.height=400;
            const g=c.getContext('2d');g.fillStyle='#176553';g.fillRect(40,40,320,320);
            for(const img of document.querySelectorAll('.stage-bg'))img.src=c.toDataURL('image/png')}""")
        seen=set()
        for section,action in [('control',None),('editor',None),('setup','main:set'),('setup','main:adjust'),('setup','period:set')]:
            navigate(page,section)
            if action:choose(page,'builderAction',action)
            no_overflow(page)
            assert page.locator('input[type="range"],[role="slider"]').count()==0
            for group in page.locator('.touch-stepper:visible,.value-stepper:visible').all():
                assert group.locator('xpath=ancestor::fieldset[contains(@class,"number-group")]/legend').inner_text().strip()
                parts=group.locator(':scope > *');assert parts.count()==3
                bounds=[parts.nth(i).bounding_box() for i in range(3)]
                value=parts.nth(1);id=value.get_attribute('id');seen.add(id)
                for box in bounds:assert box['height']==64,(width,id,bounds)
                assert bounds[0]['width']==64 and bounds[2]['width']==64,(width,id,bounds)
                for i in [0,1]:assert abs(bounds[i+1]['x']-(bounds[i]['x']+bounds[i]['width'])-10)<.1,(width,id,bounds)
                style=value.evaluate('e=>{const c=getComputedStyle(e);return {size:parseFloat(c.fontSize),radius:c.borderRadius,border:c.borderLeftWidth}}')
                assert style=={'size':28,'radius':'9px','border':'1px'},(width,id,style)
                fits=value.evaluate('''(e,text)=>{const c=getComputedStyle(e),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=c.font;
                    return ctx.measureText(text).width<=e.clientWidth-parseFloat(c.paddingLeft)-parseFloat(c.paddingRight)}''',limits[id])
                assert fits,(width,id,'allowed value would clip',bounds[1])
            if section=='editor':
                button=page.locator('#selectBackground')
                assert button.inner_text()=='Edit background — move & resize'
                assert button.bounding_box()['height']>=64
                assert page.locator('#backgroundEditHelp').inner_text()=='Select to drag the graphic or resize it using the corner handles.'
                assert button.bounding_box()['y']+button.bounding_box()['height']<page.locator('#editorFrame').bounding_box()['y']
                button.focus();page.keyboard.press('Space')
                assert button.inner_text()=='Finish editing background'
                assert button.get_attribute('aria-pressed')=='true'
                assert page.locator('.background-resize-handle:visible').count()==4
                assert page.locator('#unsavedBadge').is_hidden(),'selection alone dirtied the layout'
                page.keyboard.press('Escape');assert button.get_attribute('aria-pressed')=='false'
                assert page.locator('.background-resize-handle:visible').count()==0
            page.evaluate('scrollTo(0,0)')
            suffix='-'+action.replace(':','-') if action and action!='main:set' else ''
            page.screenshot(path=str(root/f'.test/numeric-{section}{suffix}-{width}px.png'),full_page=True)
            if width==1920:page.screenshot(path=str(root/f'.test/maximized-{section}{suffix}-1920x1080.png'))
            for stepper in page.locator('.touch-stepper:visible').all():
                value=stepper.locator('input');initial=float(value.input_value())
                stepper.locator('button').last.focus();page.keyboard.press('Enter')
                assert abs(float(value.input_value())-initial-1)<.001,(width,value.get_attribute('id'))
                stepper.locator('button').first.focus();page.keyboard.press('Space')
                assert abs(float(value.input_value())-initial)<.001,(width,value.get_attribute('id'))
        assert seen==set(limits),(width,seen)
        posts=page.evaluate('window.__posts.length')
        page.locator('#networkPort').fill('65535');page.locator('[data-number-step="networkPort:1"]').click()
        page.wait_for_timeout(300);assert page.locator('#networkPort').input_value()=='65535'
        page.locator('#builderPeriod').fill('20');page.locator('[data-number-step="builderPeriod:1"]').click()
        assert page.locator('#builderPeriod').input_value()=='20'
        choose(page,'builderAction','main:adjust');page.locator('#builderDelta').fill('-10')
        page.locator('[data-number-step="builderDelta:-1"]').click();assert page.locator('#builderDelta').input_value()=='-11'
        assert json.loads(page.locator('#builderBody').inner_text())=={'seconds':-11}
        assert page.evaluate('window.__posts.length')==posts,'configuration/builder step applied a live action'
        # All five live numbers keep immediate +/- and exact prompt behavior,
        # now using native buttons for Enter/Space and focus visibility.
        navigate(page,'control')
        for field,id,value in [('home_score','homeScore',999),('away_score','awayScore',321),('home_fouls','homeFouls',30),('away_fouls','awayFouls',11),('period','periodValue',20)]:
            name=page.locator('#'+id+'Label').inner_text()+' '+page.locator('#'+id).inner_text()
            assert page.get_by_role('button',name=name,exact=True).count()==1,(id,'accessible name')
            page.locator('#'+id).focus();page.once('dialog',lambda d,v=value:d.accept(str(v)));page.keyboard.press('Enter')
            page.wait_for_function('(x)=>window.__mock[x[0]]===x[1]',arg=[field,value])
            page.locator(f'[data-adjust="{field}:-1"]').focus();page.keyboard.press('Space')
            page.wait_for_function('(x)=>window.__mock[x[0]]===x[1]',arg=[field,value-1])
            page.locator(f'[data-adjust="{field}:1"]').click()
            page.wait_for_function('(x)=>window.__mock[x[0]]===x[1]',arg=[field,value])
        # Duration edits remain pending, including blank/zero values.
        duration=page.evaluate('window.__mock.main.duration_seconds')
        page.locator('#mainMinutes').fill('0');page.locator('#mainSeconds').fill('')
        navigate(page,'editor');page.wait_for_timeout(600);navigate(page,'control')
        assert page.locator('#mainMinutes').input_value()=='0' and page.locator('#mainSeconds').input_value()==''
        assert page.evaluate('window.__mock.main.duration_seconds')==duration
        assert not errors,errors
        page.close()
        print('23 consistent numeric groups, full allowed values, keyboard exact entry, background toggle:',width,'PASS')
