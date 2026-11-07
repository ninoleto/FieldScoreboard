"""Native simulated coverage of foul/period ownership and OT semantics."""
import json,time
from urllib.error import HTTPError

def verify_seven(request,wait_for,fixture,entered):
    targets=('main','shot','home_score','away_score','home_fouls','away_fouls','period')
    def command(action,t):return request('/api/ocr/'+action,{'target':t})
    def reject(path,body):
        try:request(path,body)
        except HTTPError as e:assert e.code==400 and 'manual control' in json.load(e)['error'];return
        raise AssertionError(path+' bypassed ownership')
    fixture.update(text='05:00',shot='24',home='10',away='9',home_fouls='3',away_fouls='2',period='4')
    wait_for(lambda s:all(s['ocr']['targets'][t]['can_follow'] for t in targets) and s['ocr']['targets']['period']['last_accepted']=='4')
    request('/api/game',{'field':'period_overtime','value':True})
    for t in targets:command('follow',t)
    state=wait_for(lambda s:s['home_fouls']==3 and s['away_fouls']==2 and s['period']==4)
    assert state['period_label']=='OT'
    overlay=request('/api/overlay-state')
    for key in ('home_fouls','away_fouls','period','period_label'):assert overlay[key]==state[key]
    for t in ('home_fouls','away_fouls','period'):
        reject('/api/game',{'field':t,'value':1});reject('/api/adjust',{'field':t,'delta':1})
    for t in targets:command('manual',t)
    for t in ('home_fouls','away_fouls','period'):
        command('follow',t);before=request('/api/state');reject('/api/reset-game',{});after=request('/api/state')
        for key in ('home_score','away_score','home_fouls','away_fouls','period','period_overtime'):assert before[key]==after[key]
        command('manual',t)
    for t in ('home_fouls','away_fouls','period'):command('follow',t)
    fixture.update(home_fouls='31',away_fouls='30',period='0')
    state=wait_for(lambda s:s['away_fouls']==30 and s['ocr']['targets']['period']['reading']=='malformed')
    assert state['home_fouls']==3 and state['period']==4 and state['period_label']=='OT'
    fixture.update(home_fouls='0',period='20')
    wait_for(lambda s:s['home_fouls']==0 and s['period']==20)
    request('/api/game',{'field':'period_overtime','value':False})
    assert request('/api/state')['period_label']=='20'
    request('/api/game',{'field':'period_overtime','value':True})
    entered.clear();fixture.update(home_fouls='7',away_fouls='8',period='3',delay=.45);assert entered.wait(2)
    command('manual','home_fouls');command('manual','period');fixture['delay']=0
    state=wait_for(lambda s:s['away_fouls']==8)
    assert state['home_fouls']==0 and state['period']==20 and state['period_label']=='OT'
    command('manual','away_fouls')
    print('SIMULATED seven-field: updates, foul/period limits, API/exact/+/- ownership, atomic resets, late takeover and manual OT/saved period PASS',flush=True)
