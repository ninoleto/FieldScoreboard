"""Fine-position regression: selected-step movement and precise scalar steppers."""
from ui_touch_checks import navigate, no_overflow


def verify_fine_position(browser, offline_page, root):
    for width,touch in [(375,True),(1920,False)]:
        page,errors=offline_page(browser,width,1080,has_touch=touch)
        page.wait_for_function("document.getElementById('connected').classList.contains('ok')")
        navigate(page,'editor')
        activate=lambda button:button.tap() if touch else button.click()
        def position(x,y):
            for id,value in [('elementX',x),('elementY',y)]:
                page.locator('#'+id).fill(str(value));page.locator('#'+id).blur()
        def xy():
            return [int(page.locator('#'+id).input_value()) for id in ['elementX','elementY']]
        assert page.locator('[data-nudge-size]').all_text_contents()==['5 px','10 px','20 px']
        assert page.locator('[data-nudge-size].active').get_attribute('data-nudge-size')=='5'
        assert page.locator('[data-nudge-size][aria-pressed="true"]').count()==1
        page.locator('[data-field="home_score"]').click()
        position(960,540);activate(page.locator('[data-nudge="right"]'));assert xy()==[965,540]
        for step in [5,10,20]:
            activate(page.locator(f'[data-nudge-size="{step}"]'))
            assert page.locator('[data-nudge-size].active').count()==1
            assert page.locator('[data-nudge-size][aria-pressed="true"]').get_attribute('data-nudge-size')==str(step)
            for direction,dx,dy in [('up',0,-1),('left',-1,0),('down',0,1),('right',1,0)]:
                arrow=page.locator(f'[data-nudge="{direction}"]')
                assert arrow.bounding_box()['height']>=49
                position(960,540);activate(arrow)
                assert xy()==[960+dx*step,540+dy*step],(width,step,direction,xy())
                # Cross a boundary and then press again at that boundary.
                start=[2 if dx<0 else 1918 if dx>0 else 960,2 if dy<0 else 1078 if dy>0 else 540]
                expected=[0 if dx<0 else 1920 if dx>0 else 960,0 if dy<0 else 1080 if dy>0 else 540]
                position(*start);activate(arrow);assert xy()==expected,(width,step,direction,'crossing')
                activate(arrow);assert xy()==expected,(width,step,direction,'at edge')
            position(960,540)
            for axis,index in [('elementX',0),('elementY',1)]:
                for delta in [-1,1]:
                    before=xy();activate(page.locator(f'[data-element-step="{axis}:{delta}"]'))
                    expected=before.copy();expected[index]+=delta
                    assert xy()==expected,(step,axis,delta,xy())
                # Precision buttons also clamp, independently of the pad step.
                page.locator('#'+axis).fill('0');page.locator('#'+axis).blur()
                activate(page.locator(f'[data-element-step="{axis}:-1"]'));assert xy()[index]==0
                maximum=1920 if index==0 else 1080
                page.locator('#'+axis).fill(str(maximum));page.locator('#'+axis).blur()
                activate(page.locator(f'[data-element-step="{axis}:1"]'));assert xy()[index]==maximum
            # Selecting a movement step must not turn font +/- into jumps.
            for id in ['elementSize']:
                before=int(page.locator('#'+id).input_value())
                activate(page.locator(f'[data-element-step="{id}:1"]'))
                assert int(page.locator('#'+id).input_value())==before+1
                activate(page.locator(f'[data-element-step="{id}:-1"]'))
        # Keyboard activation uses the selected pad step; existing canvas-key
        # shortcuts remain one pixel (Shift: ten), independent of this selector.
        page.locator('[data-field="shot_clock"]').click();position(1000,500)
        page.locator('[data-nudge="left"]').focus();page.keyboard.press('Enter');assert xy()==[980,500]
        page.locator('[data-nudge="right"]').focus();page.keyboard.press('Space');assert xy()==[1000,500]
        page.locator('#editorStage').focus();page.keyboard.press('ArrowRight');assert xy()==[1001,500]
        page.keyboard.press('Shift+ArrowDown');assert xy()==[1001,510]
        navigate(page,'control');page.wait_for_timeout(400);navigate(page,'editor')
        assert xy()==[1001,510] and page.locator('[data-nudge-size].active').get_attribute('data-nudge-size')=='20'
        assert page.evaluate('window.__posts.length')==0,'nudge changed the live layout before Save'
        page.locator('#saveLayout').click()
        page.wait_for_function('window.__mock.layout.elements.shot_clock.x===1001 && window.__mock.layout.elements.shot_clock.y===510')
        position(2,2);activate(page.locator('[data-nudge="up"]'))
        page.once('dialog',lambda d:d.accept());page.locator('#discardLayout').click();assert xy()==[1001,510]
        no_overflow(page)
        page.locator('.nudge-tool').screenshot(path=str(root/f'.test/fine-position-{width}px.png'))
        assert not errors,errors
        page.close()
        print('Fine position 5/10/20, default 5, four directions/edges, precision +/- and Save/Discard:',width,'touch' if touch else 'mouse/keyboard','PASS')
