"""Operator wording and dynamic examples in the existing OCR choice dialog."""
import base64
import io
from PIL import Image
from playwright.sync_api import expect
from ui_touch_checks import choose, no_overflow


def verify_format_choices(page, request, wait_for, output, label, touch=False, keyboard=False):
    precision = page.locator('#ocr-main-final-formatChoice')
    appearance = page.locator('#ocr-main-final-styleChoice')
    expect(page.locator('label[for="ocr-main-auto-format"]')).to_have_text('Automatically change clock format in the final minute')
    expect(page.locator('#ocr-main-switch-help')).to_have_text('When enabled, the clock switches from minutes and seconds to seconds only below 1 minute.')
    expect(page.locator('#ocr-main-format-help')).to_have_text('ScoreSight controls the clock while Follow OCR is active. These settings only change how time is displayed. Your normal Match Clock format returns when you take manual control.')
    expect(page.locator('#ocr-main-format-off')).to_be_hidden()
    styles = ('visible', 'invisible', 'clean')
    descriptions = ['Standard minutes-and-seconds appearance.', 'Hide the leading zeros while keeping the seconds in their original position.', 'Display seconds without the minutes prefix.']

    def pick(index):
        option = page.locator(f'#touchChoiceList [data-index="{index}"]')
        assert option.bounding_box()['height'] >= 64
        if keyboard:
            page.keyboard.press('Home')
            for _ in range(index): page.keyboard.press('ArrowDown')
            expect(option).to_be_focused()
            page.keyboard.press('Enter')
        elif touch:
            # Tap the far lower-right of the whole option, outside its label.
            box = option.bounding_box()
            option.tap(position={'x': box['width'] - 12, 'y': box['height'] - 12})
        else:
            option.click()
        expect(page.locator('#touchChoiceDialog')).not_to_be_visible()

    for mode_index, (mode, caption, example) in enumerate((('SS', 'Whole seconds — 30', '30'), ('SS.t', 'Tenths of a second — 30.6', '30.6'))):
        expect(precision).to_be_enabled()
        precision.click()
        expect(page.locator('#touchChoiceHeading')).to_have_text('Time precision')
        expect(page.locator('#touchChoiceList button')).to_have_text(['Whole seconds — 30', 'Tenths of a second — 30.6'])
        assert all(b['height'] >= 64 for b in page.locator('#touchChoiceList button').evaluate_all('es=>es.map(e=>({height:e.getBoundingClientRect().height}))'))
        pick(mode_index)
        expect(precision).to_be_enabled(); expect(precision).to_be_focused()
        expect(precision).to_have_attribute('aria-label', 'Time precision: ' + caption)
        labels = ['Show zeros — 00:' + example, 'Hide zeros — :' + example, 'Seconds only — ' + example]
        for index, style in enumerate(styles):
            expect(appearance).to_be_enabled(); appearance.click()
            expect(page.locator('#touchChoiceHeading')).to_have_text('Final-minute appearance')
            for i, text in enumerate(labels):
                option = page.locator(f'#touchChoiceList [data-index="{i}"]')
                expect(option).to_contain_text(text)
                expect(option.locator('.touch-choice-description')).to_have_text(descriptions[i])
                assert option.bounding_box()['height'] >= 64
            selected = page.locator('#touchChoiceList [aria-selected="true"]')
            assert 'selected' in selected.get_attribute('class')
            assert selected.evaluate('e=>getComputedStyle(e).backgroundColor') != page.locator('#touchChoiceList [aria-selected="false"]').first.evaluate('e=>getComputedStyle(e).backgroundColor')
            no_overflow(page)
            if index == 2:
                # Capture the visible viewport directly at real browser zoom;
                # document-offset screenshots can otherwise be blank after scrolling.
                session = page.context.new_cdp_session(page)
                capture = session.send('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
                screenshot = base64.b64decode(capture['data'])
                with Image.open(io.BytesIO(screenshot)) as picture:
                    assert any(low != high for low, high in picture.convert('RGB').getextrema()), 'Blank appearance screenshot'
                (output / f'appearance-{label}-{mode}-verified.png').write_bytes(screenshot)
                session.detach()
            pick(index)
            expect(appearance).to_be_enabled(); expect(appearance).to_be_focused()
            expect(appearance).to_have_attribute('aria-label', 'Final-minute appearance: ' + labels[index])
            state = wait_for(lambda s: s['ocr']['main_time_format'] == {'enabled': True, 'final_minute_format': mode, 'final_minute_style': style})
            assert state['ocr']['main_time_format']['final_minute_format'] in ('SS', 'SS.t')

    # An external setting update while open refreshes examples without losing
    # the selected row or keyboard focus. It does not acquire OCR ownership.
    following = request('/api/state')['ocr']['following']
    appearance.click()
    request('/api/ocr/time-format', {'enabled': True, 'final_minute_format': 'SS', 'final_minute_style': 'clean'})
    expect(page.locator('#touchChoiceList [data-index="2"]')).to_contain_text('Seconds only — 30')
    expect(page.locator('#touchChoiceList [data-index="2"]')).not_to_contain_text('30.6')
    expect(page.locator('#touchChoiceList [data-index="2"]')).to_be_focused()
    page.keyboard.press('Escape'); expect(appearance).to_be_focused()
    assert request('/api/state')['ocr']['following'] == following
    # Keep the existing downstream format tests in their expected clean mode.
    choose(page, 'ocr-main-final-format', 'SS.t')
    expect(precision).to_be_enabled(); expect(precision).to_be_focused()
    print('OCR operator choices:', label, 'labels/examples, persisted values, 64px options, full-row selection, focus and live synchronization PASS', flush=True)
