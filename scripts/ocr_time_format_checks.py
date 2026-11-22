"""Automatic match OCR format checks using test_ocr's isolated source only."""
import time


def verify_time_format(request, wait_for, fixture):
    request('/api/ocr/manual', {'target': 'main'})
    request('/api/display', {'field': 'main_clock_format', 'value': 'HH:MM:SS'})
    request('/api/ocr/time-format', {'enabled': True, 'final_minute_format': 'SS'})
    fixture.update(text='01:01', state='Success', status=200, missing=False, delay=0)
    wait_for(lambda s: s['ocr']['can_follow'])
    request('/api/ocr/follow', {'target': 'main'})
    initial = request('/api/state')
    for mode in ('SS', 'SS.t'):
        request('/api/ocr/time-format', {'enabled': True, 'final_minute_format': mode})
        for source, value, whole, tenth in [
            ('01:01', 61, '01:01', '01:01'), ('01:00', 60, '01:00', '01:00'),
            ('59.9', 59.9, '59', '59.9'), ('55.4', 55.4, '55', '55.4'),
            ('55.3', 55.3, '55', '55.3'), ('0.1', .1, '00', '00.1'),
            ('0.0', 0, '00', '00.0'), ('20:00', 1200, '20:00', '20:00'),
            ('00:59', 59, '59', '59.0'), ('01:00', 60, '01:00', '01:00'),
        ]:
            fixture['text'] = source
            state = wait_for(lambda s: s['ocr']['last_accepted'] == source)
            assert state['main']['remaining_seconds'] == value
            assert state['main']['display'] == (whole if mode == 'SS' else tenth)
            assert request('/api/overlay-state')['main'] == state['main']
            assert state['layout'] == initial['layout']
            for key in ('home_score', 'away_score', 'home_fouls', 'away_fouls', 'period', 'shot'):
                assert state[key] == initial[key], key
    fixture['text'] = '55.4'
    wait_for(lambda s: s['main']['display'] == '55.4')
    time.sleep(1.2)
    assert request('/api/state')['main']['remaining_seconds'] == 55.4, 'OCR ticked independently'
    for update, reading in [({'text': '59.99'}, 'malformed'), ({'text': '0.0', 'state': 'FailedFilter'}, 'rejected'),
                            ({'state': 'Empty'}, 'rejected'), ({'missing': True}, 'missing'), ({'status': 503}, 'unavailable')]:
        fixture.update(update)
        state = wait_for(lambda s: s['ocr']['reading'] == reading)
        assert state['main']['display'] == '55.4' and state['ocr']['following']
    fixture.update(text='55.3', state='Success', status=200, missing=False)
    wait_for(lambda s: s['main']['display'] == '55.3')
    state = request('/api/ocr/manual', {'target': 'main'})
    assert state['main']['remaining_seconds'] == 55.3 and state['main']['display'] == '00:00:56'
    assert state['main']['state'] == 'paused'
    fixture['text'] = '20:00'
    time.sleep(.5)
    assert request('/api/state')['main'] == state['main']
    # Leave the original suite in its expected default display mode.
    request('/api/display', {'field': 'main_clock_format', 'value': 'MM:SS'})
    request('/api/ocr/time-format', {'enabled': False, 'final_minute_format': 'SS'})
    print('SIMULATED automatic OCR format: boundaries, tenths, holds, resets, overlay and takeover PASS', flush=True)


def verify_time_format_ui(base, request, wait_for, fixture, root):
    import base64
    import io
    import json
    import math
    import os
    import shutil
    import tempfile
    from pathlib import Path
    from PIL import Image
    from playwright.sync_api import sync_playwright, expect
    from ui_touch_checks import choose, navigate, no_overflow

    request('/api/ocr/manual', {'target': 'main'})
    fixture.update(text='01:00', state='Success', status=200, missing=False, delay=0)
    wait_for(lambda s: s['ocr']['can_follow'])
    output = root / '.test' / 'ocr-format4'
    output.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
        for width in (375, 500, 1000, 1440, 1920):
            request('/api/ocr/manual', {'target': 'main'})
            request('/api/ocr/time-format', {'enabled': False, 'final_minute_format': 'SS'})
            context = browser.new_context(viewport={'width': width, 'height': 1080}, has_touch=width == 375)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.add_init_script('''const originalFetch=window.fetch;window.fetch=async(...args)=>{
              const response=await originalFetch(...args);
              if(args[0]==='/api/ocr/time-format'&&window.__holdFormat){window.__holdFormat=false;await new Promise(resolve=>{window.__releaseFormat=resolve;window.__formatHeld=true})}
              return response;
            };''')
            page.goto(base)
            from ocr_correction_checks import verify_card_order
            verify_card_order(page, keyboard=True)
            toggle = page.locator('#ocr-main-auto-format')
            label = page.locator('label[for="ocr-main-auto-format"]')
            picker = page.locator('#ocr-main-final-formatChoice')
            expect(picker).to_be_disabled()
            expect(page.locator('#ocr-main-format-off')).to_have_text('Automatic switching is off. The clock uses your normal Match Clock output format.')
            expect(page.locator('#ocr-main-format-off')).to_be_visible()
            assert label.bounding_box()['height'] >= 64
            assert picker.bounding_box()['height'] >= 64
            label.scroll_into_view_if_needed()
            if width == 375:
                label.tap()
            elif width == 500:
                toggle.focus(); toggle.press('Space')
            else:
                label.click()
            expect(picker).to_be_enabled()
            if width == 500: expect(toggle).to_be_focused()
            assert request('/api/state')['ocr']['main_time_format']['enabled']
            from ocr_usability_checks import verify_format_choices
            verify_format_choices(page, request, wait_for, output, str(width), touch=width == 375, keyboard=width == 500)
            choose(page, 'ocr-main-final-format', 'SS.t')
            expect(picker).to_be_focused()
            wait_for(lambda s: s['ocr']['main_time_format']['final_minute_format'] == 'SS.t')
            expect(page.locator('#ocr-main-follow')).to_be_enabled()
            page.locator('#ocr-main-follow').click()
            fixture['text'] = '55.4'
            wait_for(lambda s: s['main']['display'] == '55.4')
            expect(page.locator('#previewStage [data-id="main_clock"]')).to_have_text('55.4')
            overlay = context.new_page(); overlay.goto(base + '/overlay')
            expect(overlay.locator('[data-id="main_clock"]')).to_have_text('55.4')
            overlay.close()
            # Polling must preserve the focused format control, scroll and drafts.
            picker.focus(); position = page.evaluate('scrollY'); page.wait_for_timeout(650)
            expect(picker).to_be_focused()
            assert abs(page.evaluate('scrollY') - position) < 2
            assert page.locator('#ocr-main-final-format').get_attribute('tabindex') == '-1'
            navigate(page, 'editor')
            page.locator('#elementX').fill('777')
            page.locator('#elementX').blur()
            navigate(page, 'control')
            if width == 1920: page.evaluate('window.__holdFormat=true')
            choose(page, 'ocr-main-final-format', 'SS')
            if width == 1920:
                page.wait_for_function('()=>window.__formatHeld')
                expect(picker).to_be_disabled()
                page.locator('#homeName').focus()
                page.evaluate('window.__releaseFormat()')
                expect(picker).to_be_enabled()
                expect(page.locator('#homeName')).to_be_focused()
            wait_for(lambda s: s['main']['display'] == '55')
            navigate(page, 'editor')
            assert page.locator('#elementX').input_value() == '777'
            page.locator('#discardLayout').click()
            navigate(page, 'control')
            no_overflow(page)
            assert page.evaluate('''()=>{const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return new Set(ids).size===ids.length}''')
            page.locator('.ocr-time-format').scroll_into_view_if_needed()
            page.screenshot(path=str(output / f'controls-{width}.png'))
            # Takeover restores the saved manual format without changing 55.4.
            page.locator('#ocr-main-manual').click()
            wait_for(lambda s: s['main']['state'] == 'paused')
            assert request('/api/state')['main']['remaining_seconds'] == 55.4
            assert request('/api/state')['main']['display'] == '00:56'
            page.reload(); expect(toggle).to_be_checked()
            assert not errors, errors
            fixture['text'] = '01:00'
            context.close()
        browser.close()
    # Real Chromium page zoom, using the same preference as the offline suite.
    with sync_playwright() as p:
        for zoom in (2, 4):
            with tempfile.TemporaryDirectory(dir=output) as folder:
                profile = Path(folder) / 'Default'; profile.mkdir()
                (profile / 'Preferences').write_text(json.dumps({'partition': {'default_zoom_level': {'x': math.log(zoom) / math.log(1.2)}}}), encoding='utf-8')
                context = p.chromium.launch_persistent_context(folder, headless=True, viewport={'width': 1920, 'height': 1080}, executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome') or p.chromium.executable_path)
                page = context.pages[0]; page.goto(base)
                assert page.evaluate('innerWidth') == 1920 / zoom
                assert abs(page.evaluate('devicePixelRatio') - zoom) < .01
                verify_card_order(page)
                page.locator('.ocr-time-format').scroll_into_view_if_needed()
                no_overflow(page)
                verify_format_choices(page, request, wait_for, output, f'zoom-{zoom * 100}', keyboard=True)
                # At native zoom, Playwright's document-offset clip can capture
                # outside the surface after scrolling. Capture the visible
                # viewport directly and reject blank visual evidence.
                session = context.new_cdp_session(page)
                capture = session.send('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
                screenshot = base64.b64decode(capture['data'])
                with Image.open(io.BytesIO(screenshot)) as picture:
                    assert any(low != high for low, high in picture.convert('RGB').getextrema()), 'Blank zoom screenshot'
                (output / f'zoom-{zoom * 100}.png').write_bytes(screenshot)
                session.detach()
                choose(page, 'ocr-main-final-format', 'SS.t')
                expect(page.locator('#ocr-main-final-formatChoice')).to_be_focused()
                context.close()
    request('/api/ocr/time-format', {'enabled': True, 'final_minute_format': 'SS.t'})
    print('Automatic OCR format UI: widths, touch/keyboard, delayed-write focus, polling, layout drafts, preview/OBS, reload and 200%/400% zoom PASS', flush=True)
