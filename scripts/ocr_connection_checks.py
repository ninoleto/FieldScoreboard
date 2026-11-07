"""Native, simulated-source disconnect/reconnect and canceled-response checks."""
import time

TARGETS=('main','shot','home_score','away_score','home_fouls','away_fouls','period')

def verify_connection(request,wait_for,fixture,entered):
    address=request('/api/state')['ocr']['address']
    fixture.update(text='03:21',shot='14',home='35',away='27',home_fouls='4',away_fouls='2',period='3',status=200,state='Success',missing=False,delay=0)
    request('/api/ocr/disconnect',{})
    request('/api/ocr/connect',{'address':address})
    wait_for(lambda s:all(v['can_follow'] for v in s['ocr']['targets'].values()))
    for target in TARGETS:request('/api/ocr/follow',{'target':target})
    before=request('/api/state');mappings={k:v['field'] for k,v in before['ocr']['targets'].items()}
    def held(s):
        for key in TARGETS:
            if key in ('main','shot'):
                assert s[key]['display']==before[key]['display'] and s[key]['state']=='paused',(key,s[key],before[key])
            else:assert s[key]==before[key],key
        assert not any(v['following'] for v in s['ocr']['targets'].values())
        assert {k:v['field'] for k,v in s['ocr']['targets'].items()}==mappings
        assert s['ocr']['address']==address
    # Source snapshots a response before Disconnect; it returns changed values later.
    fixture.update(text='01:11',shot='9',home='99',away='88',home_fouls='8',away_fouls='7',period='5',delay=.6)
    entered.clear();assert entered.wait(3),'no in-flight source request'
    held(request('/api/ocr/disconnect',{}));count=fixture['requests']
    time.sleep(1.2)
    state=request('/api/state');held(state)
    assert state['ocr']['connection']=='disconnected' and not state['ocr']['monitoring']
    assert fixture['requests']==count,'backend continued polling'
    fixture['delay']=0
    request('/api/ocr/connect',{'address':address})
    state=wait_for(lambda s:all(v['can_follow'] for v in s['ocr']['targets'].values()))
    held(state)
    for target in TARGETS:request('/api/ocr/follow',{'target':target})
    state=wait_for(lambda s:s['home_score']==99 and s['main']['display']=='01:11')
    assert all(v['following'] for v in state['ocr']['targets'].values())
    # Explicit retry after a loss also requires new ownership, even without Disconnect.
    fixture['status']=503
    state=wait_for(lambda s:s['ocr']['connection']=='error');before=state
    request('/api/ocr/connect',{'address':address});fixture['status']=200
    state=wait_for(lambda s:s['ocr']['connection']=='connected');held(state)
    # Stop a pending initial connection as well.
    request('/api/ocr/disconnect',{});fixture['delay']=.6;entered.clear()
    request('/api/ocr/connect',{'address':address});assert entered.wait(3)
    held(request('/api/ocr/disconnect',{}));time.sleep(.8)
    assert request('/api/state')['ocr']['connection']=='disconnected'
    fixture['delay']=0;request('/api/ocr/connect',{'address':address})
    wait_for(lambda s:s['ocr']['connection']=='connected')
    print('Disconnect: seven held values, paused owned clocks, canceled response, stopped polling, saved settings, explicit reconnect/follow, pending cancellation PASS',flush=True)
