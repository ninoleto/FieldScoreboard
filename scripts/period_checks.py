"""Native period normalization/display checks using the shared OCR simulator."""
import json
from urllib.error import HTTPError

def label(n,format):
    suffix='th' if 11<=n%100<=13 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')
    return str(n)+suffix if format=='ordinal' else 'Q'+str(n) if format=='quarter' else str(n)

def verify_period_formats(request,wait_for,fixture):
    def game(field,value):return request('/api/game',{'field':field,'value':value})
    def check(n,format,ot=False):
        s=request('/api/state');o=s['ocr']['targets']['period'];overlay=request('/api/overlay-state')
        assert s['period']==n and s['period_format']==format and s['period_label']==('OT' if ot else label(n,format)),s
        assert overlay['period']==n and overlay['period_label']==s['period_label']
        return s,o
    def reject(field,value):
        before=request('/api/state')
        try:game(field,value)
        except HTTPError as e:assert e.code==400
        else:raise AssertionError('Invalid API value accepted')
        after=request('/api/state')
        for key in ('period','period_label','period_format','period_overtime'):assert after[key]==before[key]
    request('/api/ocr/manual',{'target':'period'});game('period_overtime',False)
    assert request('/api/state')['period_format']=='number'
    for format in ('number','ordinal','quarter'):
        game('period_format',format)
        for n in (1,2,3,11,12,13,20):game('period',n);check(n,format)
        game('period',12);request('/api/adjust',{'field':'period','delta':1});check(13,format)
        for invalid in ('3rd','Q3',0,21,3.5):reject('period',invalid)
    for invalid in ('',None,'roman','Number',3,True):reject('period_format',invalid)
    game('period_format','number');request('/api/profiles',{'name':'Period formatting','action':'save'})
    game('period_format','quarter');game('period',11);request('/api/profiles',{'name':'Period formatting','action':'load'});check(11,'quarter')
    fixture['period']='3rd';wait_for(lambda s:s['ocr']['targets']['period']['recognized']=='3rd' and s['ocr']['targets']['period']['can_follow'])
    request('/api/ocr/follow',{'target':'period'})
    for format in ('number','ordinal','quarter'):
        game('period_format',format)
        for raw,n in [('3',3),('3rd',3),('Q3',3),(' 1ST ',1),('2nd',2),('11th',11),('12TH',12),('\tq13 ',13),('20th',20)]:
            fixture['period']=raw
            wait_for(lambda s:s['period']==n and s['ocr']['targets']['period']['recognized']==raw)
            s,o=check(n,format);assert o['following'] and o['last_accepted']==str(n) and o['reading']=='accepted'
        game('period_overtime',True);fixture['period']='Q13';wait_for(lambda s:s['period']==13);check(13,format,True)
        game('period_overtime',False);check(13,format)
    for raw in ('3th','11st','12nd','13rd','Q3rd','Period 3','3rd quarter','Q 3','3 rd','+3','3.0','0','21','Q21','21st',''):
        fixture['period']=raw;wait_for(lambda s:s['ocr']['targets']['period']['recognized']==raw and s['ocr']['targets']['period']['reading']=='malformed')
        s,o=check(13,'quarter');assert o['last_accepted']=='13' and 'valid ordinal' in o['warning']
    fixture.update(period='2nd',period_state='FailedFilter');wait_for(lambda s:s['ocr']['targets']['period']['reading']=='rejected');check(13,'quarter')
    fixture.update(period_state='Success',period_missing=True);wait_for(lambda s:s['ocr']['targets']['period']['reading']=='missing');check(13,'quarter')
    fixture.update(period_missing=False,period='Q3');wait_for(lambda s:s['period']==3);check(3,'quarter')
    request('/api/ocr/manual',{'target':'period'});fixture['period']='4th'
    wait_for(lambda s:s['ocr']['targets']['period']['recognized']=='4th');check(3,'quarter')
    assert not request('/api/state')['ocr']['targets']['period']['following']
    print('SIMULATED period: numeric/ordinal/quarter normalization, independent formats, API limits, invalid hold, OT, presets and takeover PASS',flush=True)
