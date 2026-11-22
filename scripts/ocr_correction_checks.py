"""Recognition/output independence and the requested ScoreSight reading order."""
import time


def verify_recognition_formats(request, wait_for, fixture):
    request('/api/ocr/manual', {'target': 'main'})
    request('/api/ocr/time-format', {'enabled': False, 'final_minute_format': 'SS', 'final_minute_style': 'clean'})
    initial = request('/api/state')
    fixture.update(text='48.2', state='Success', status=200, missing=False, delay=0)
    state = wait_for(lambda s: s['ocr']['last_accepted'] == '48.2')
    assert state['main'] == initial['main'] and not state['ocr']['following']
    request('/api/ocr/follow', {'target': 'main'})
    for format, expected in [('MM:SS', '00:49'), ('M:SS', '0:49'), ('HH:MM:SS', '00:00:49'), ('SS', '49'), ('MM:SS.t', '00:48.2')]:
        request('/api/display', {'field': 'main_clock_format', 'value': format})
        for enabled in (False, True, False):
            for precision in ('SS', 'SS.t'):
                for style, prefix in [('visible', '00:'), ('invisible', ':'), ('clean', '')]:
                    state = request('/api/ocr/time-format', {'enabled': enabled, 'final_minute_format': precision, 'final_minute_style': style})
                    want = prefix + ('48.2' if precision == 'SS.t' else '48') if enabled else expected
                    assert state['main']['remaining_seconds'] == 48.2 and state['main']['display'] == want
                    assert state['ocr']['following'] and state['layout']['main_clock_format'] == format
                    assert request('/api/overlay-state')['main'] == state['main']
        fixture['text'] = '48.1'
        wait_for(lambda s: s['main']['remaining_seconds'] == 48.1)
        fixture['text'] = '48.2'
        state = wait_for(lambda s: s['main']['remaining_seconds'] == 48.2)
        for update, reading in [({'text': '48.22'}, 'malformed'), ({'text': '00:48.2'}, 'malformed'),
                                ({'text': '0.0', 'state': 'FailedFilter'}, 'rejected'), ({'missing': True}, 'missing'), ({'status': 503}, 'unavailable')]:
            fixture.update(update)
            held = wait_for(lambda s: s['ocr']['reading'] == reading)
            assert held['main'] == state['main'] and held['ocr']['following']
        fixture.update(text='48.2', state='Success', status=200, missing=False)
        wait_for(lambda s: s['ocr']['reading'] == 'accepted')
    time.sleep(.5)
    assert request('/api/state')['main']['remaining_seconds'] == 48.2
    request('/api/ocr/manual', {'target': 'main'})
    request('/api/display', {'field': 'main_clock_format', 'value': 'MM:SS'})
    request('/api/ocr/time-format', {'enabled': False, 'final_minute_format': 'SS', 'final_minute_style': 'clean'})
    print('Recognition/output independence: five manual formats x toggle x precision x style, explicit follow, exact holds/loss/recovery PASS', flush=True)


def verify_card_order(page, keyboard=False):
    order = ['home_score', 'away_score', 'home_fouls', 'away_fouls', 'period', 'shot', 'main']
    cards = page.locator('.ocr-targets > .ocr-target')
    assert cards.evaluate_all("es=>es.map(e=>e.getAttribute('aria-labelledby'))") == [f'ocr-{key}-heading' for key in order]
    boxes = [card.bounding_box() for card in cards.all()]
    grid = page.locator('.ocr-targets').bounding_box()
    if page.evaluate('innerWidth') > 1100:
        for i in (0, 2, 4):
            assert abs(boxes[i]['y'] - boxes[i+1]['y']) < 1
            assert boxes[i+1]['x'] >= boxes[i]['x'] + boxes[i]['width'] + 23
            if i: assert boxes[i]['y'] >= max(b['y']+b['height'] for b in boxes[i-2:i]) + 23
        assert boxes[6]['y'] >= max(b['y']+b['height'] for b in boxes[4:6]) + 23
    else:
        for a, b in zip(boxes, boxes[1:]): assert b['y'] >= a['y'] + a['height'] + 23
    assert abs(boxes[-1]['width'] - grid['width']) < 1 and abs(boxes[-1]['x'] - grid['x']) < 1
    if keyboard:
        controls = cards.locator('button:enabled, input:enabled').all()
        controls = [c for c in controls if c.is_visible() and c.evaluate('e=>e.tabIndex>=0')]
        controls[0].focus()
        for control in controls:
            assert control.evaluate('e=>e===document.activeElement'), control.get_attribute('id')
            page.keyboard.press('Tab')
