"""Simulated native HTTP regressions for independent OCR mappings."""
import json,time
from urllib.error import HTTPError

TARGETS=('main','shot','home_score','away_score')

def verify_mappings(request,wait_for,fixture,entered):
    def command(action,target):return request('/api/ocr/'+action,{'target':target})
    def rejected(path,body):
        try:request(path,body)
        except HTTPError as error:
            assert error.code==400
            detail=json.load(error)['error']
            assert 'manual control' in detail,detail
            return
        raise AssertionError('Ownership bypass: '+path)
    fixture.update(text='05:00',state='Success',home='12',shot='24',away='7',missing=False,status=200)
    wait_for(lambda s:all(s['ocr']['targets'][t]['can_follow'] for t in TARGETS))
    command('follow','main');command('follow','home_score')
    assert request('/api/state')['shot']['state']=='ready'
    request('/api/clock/shot/start',{})
    request('/api/clock/shot/reset',{})
    assert request('/api/state')['shot']['state']=='ready','infer source running from OCR'
    request('/api/game',{'field':'away_score','value':3})
    rejected('/api/game',{'field':'home_score','value':99})
    rejected('/api/adjust',{'field':'home_score','delta':1})
    for t in ('shot','away_score'):command('follow',t)
    wait_for(lambda s:s['main']['display']=='05:00' and s['shot']['remaining_seconds']==24 and s['home_score']==12 and s['away_score']==7)
    fixture.update(text='20:00',shot='30',home='25',away='18')
    wait_for(lambda s:s['main']['display']=='20:00' and s['shot']['remaining_seconds']==30 and s['home_score']==25 and s['away_score']==18)
    overlay=request('/api/overlay-state');state=request('/api/state')
    assert 'ocr' not in overlay
    for key in ('main','shot','home_score','away_score'):assert overlay[key]==state[key],('effective overlay value',key)
    time.sleep(.7)
    assert request('/api/state')['main']['display']=='20:00' and request('/api/state')['shot']['remaining_seconds']==30
    for target in ('main','shot','both'):
        for action in ('start','pause','stop','reset'):rejected(f'/api/clock/{target}/{action}',{})
    for target in ('main','shot'):
        rejected(f'/api/clock/{target}/set',{'seconds':60,'direction':'down'})
        rejected(f'/api/clock/{target}/adjust',{'seconds':1})
    rejected('/api/reset-game',{})
    fixture.update(text='bad',shot='14',home='1000',away='19')
    state=wait_for(lambda s:s['ocr']['targets']['main']['reading']=='malformed' and s['away_score']==19)
    assert state['main']['display']=='20:00' and state['shot']['remaining_seconds']==14 and state['home_score']==25
    fixture.update(missing=True,home='26',away='20')
    state=wait_for(lambda s:s['ocr']['targets']['main']['reading']=='missing' and s['home_score']==26)
    assert state['main']['display']=='20:00'
    fixture.update(status=503)
    state=wait_for(lambda s:s['ocr']['connection']=='error')
    held=(state['main']['display'],state['shot']['display'],state['home_score'],state['away_score'])
    time.sleep(.5);state=request('/api/state')
    assert held==(state['main']['display'],state['shot']['display'],state['home_score'],state['away_score'])
    fixture.update(status=200,missing=False,text='00:00',shot='0',home='0',away='0')
    wait_for(lambda s:s['main']['display']=='00:00' and s['shot']['remaining_seconds']==0 and s['home_score']==0 and s['away_score']==0)
    fixture.update(text='05:00',shot='24',home='12',away='7')
    wait_for(lambda s:s['main']['display']=='05:00' and s['home_score']==12)
    # Freeze a response before it reaches the app; take over two targets only.
    entered.clear();fixture.update(text='00:01',shot='13',home='99',away='8',delay=.45)
    assert entered.wait(2)
    started=time.monotonic();command('manual','main');command('manual','home_score')
    assert time.monotonic()-started<.35,'manual takeover blocked on ScoreSight'
    fixture['delay']=0
    state=wait_for(lambda s:s['shot']['remaining_seconds']==13 and s['away_score']==8)
    assert state['main']['display']=='05:00' and state['main']['state']=='paused' and state['home_score']==12
    request('/api/game',{'field':'home_score','value':33})
    time.sleep(.5);assert request('/api/state')['home_score']==33
    request('/api/clock/main/start',{})
    rejected('/api/clock/both/pause',{})
    assert request('/api/state')['main']['state']=='running'
    command('manual','shot')
    assert request('/api/state')['shot']['state']=='paused'
    request('/api/clock/shot/reset',{})
    assert request('/api/state')['shot']['state']=='running'
    request('/api/clock/both/pause',{})
    command('manual','away_score')
    for t in TARGETS:assert not request('/api/state')['ocr']['targets'][t]['following']
    # Explicit unconfiguration persists and is not replaced by suggestions.
    request('/api/ocr/field',{'target':'away_score','field':''})
    time.sleep(.4)
    assert request('/api/state')['ocr']['targets']['away_score']['field']==''
    request('/api/ocr/field',{'target':'away_score','field':'Away Score'})
    print('SIMULATED multi-field: simultaneous/mixed ownership, per-field validation, API guards, atomic combined rejection, delayed takeover, loss/recovery, zero/reset and manual shot behaviour PASS',flush=True)
