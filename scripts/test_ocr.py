"""Native ScoreSight integration regression; --ui adds Chromium, --live-address reads a real source.

Always uses an isolated Field Scoreboard config/port. Never changes the OCR source.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse, json, os, shutil, socket, subprocess, tempfile, threading, time
import urllib.request

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('binary')
parser.add_argument('--ui',action='store_true')
parser.add_argument('--live-address')
args=parser.parse_args()
if args.ui and args.live_address:parser.error('--ui uses simulated fields; run live observations separately')
root=Path(__file__).resolve().parents[1]
binary=Path(args.binary).resolve()
(root/'.test').mkdir(exist_ok=True)
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'

def request(path,body=None):
    data=None if body is None else json.dumps(body).encode()
    with urllib.request.urlopen(urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'}),timeout=3) as response:
        return json.load(response)

def wait_for(predicate,timeout=5):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        state=request('/api/state')
        if predicate(state):return state
        time.sleep(.05)
    raise AssertionError('Timed out: '+json.dumps(state.get('ocr',{})))

fixture={'text':'12:34','state':'SameNoChange','status':200,'missing':False,'extra':False,'home':'999','shot':'00:01','away':'7','delay':0,'home_fouls':'3','away_fouls':'2','period':'4'}
entered=threading.Event()
class Source(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        assert self.path=='/json' and self.headers.get('Authorization') is None
        state=fixture.copy()
        payload=[] if state['missing'] else [{'name':'Time','text':state['text'],'state':state['state'],'rect':{'x':1,'y':2,'width':100,'height':50}}]
        # Discovered fields stay manual until individually followed.
        payload += [{'name':'Home Score','text':state['home'],'state':'Success'},{'name':'Shot Clock','text':state['shot'],'state':'Success'}]
        payload.append({'name':'Away Score','text':state['away'],'state':'Success'})
        for key,name in [('home_fouls','Home Fouls'),('away_fouls','Away Fouls'),('period','Period')]:payload.append({'name':name,'text':state[key],'state':'Success'})
        if state['delay']:entered.set();time.sleep(state['delay'])
        if state['extra']:payload.append({'name':'Alternate','text':'03:21','state':'Success'})
        self.send_response(state['status']);self.send_header('Content-Type','application/json');self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

source=ThreadingHTTPServer(('127.0.0.1',0),Source)
threading.Thread(target=source.serve_forever,daemon=True).start()
address=args.live_address or f'http://127.0.0.1:{source.server_port}'

with tempfile.TemporaryDirectory() as folder:
    config=Path(folder)/'config.json'
    with (Path(folder)/'server.log').open('wb') as log:
        def start():
            process=subprocess.Popen([str(binary),'--config',str(config),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            for _ in range(80):
                try:request('/api/state');return process
                except OSError:time.sleep(.05)
            raise AssertionError('Native test process did not start')
        proc=start()
        try:
            original=request('/api/state')
            request('/api/ocr/connect',{'address':address})
            state=wait_for(lambda s:s['ocr']['can_follow'])
            assert state['ocr']['field']=='Time' and state['main']==original['main']
            assert state['ocr']['freshness']=='unavailable'
            request('/api/ocr/follow',{})
            state=wait_for(lambda s:s['main']['state']=='ocr')
            if args.live_address:
                values=[];statuses=set()
                for _ in range(40):
                    state=request('/api/state');values.append(state['main']['display']);statuses.add(state['ocr']['detection_state'])
                    assert state['main']['state']=='ocr' and state['ocr']['following']
                    time.sleep(.2)
                print('LIVE observation:',json.dumps({'samples':len(values),'distinct_values':len(set(values)),'first':values[0],'last':values[-1],'states':sorted(statuses),'fields':state['ocr']['fields'],'freshness':state['ocr']['freshness']}))
            else:
                for text in ('12:33','12:33','20:00','00:00','04:59'):
                    fixture['text']=text
                    wait_for(lambda s:s['main']['display']==text)
                time.sleep(1.2)
                assert request('/api/state')['main']['display']=='04:59','independent countdown during source pause'
                for update,reading in [({'text':'00:00','state':'FailedFilter'},'rejected'),({'text':'','state':'Empty'},'rejected'),({'text':'99:99','state':'Success'},'malformed'),({'missing':True},'missing'),({'status':503},'unavailable')]:
                    fixture.update(update)
                    state=wait_for(lambda s:s['ocr']['reading']==reading)
                    assert state['main']['display']=='04:59' and (state['ocr']['warning'] or state['ocr']['connection_warning'])
                fixture.update(text='00:20',state='Success',missing=False,status=200)
                wait_for(lambda s:s['main']['display']=='00:20')
                request('/api/game',{'field':'shot_auto_hide','value':True})
                assert not request('/api/state')['shot_visible']
                fixture['text']='00:30';wait_for(lambda s:s['shot_visible'])
                assert 'ocr' not in request('/api/overlay-state')
                assert request('/api/overlay-state')['main']['display']==request('/api/state')['main']['display']
            manual=request('/api/ocr/manual',{})
            held=manual['main']['display']
            assert manual['main']['state']=='paused'
            if not args.live_address:fixture['text']='00:01'
            time.sleep(1.1)
            state=request('/api/state')
            assert state['main']['display']==held and not state['ocr']['following']
            for key in ('home_score','away_score','home_fouls','away_fouls','period','period_overtime','home_name','away_name','shot'):
                assert state[key]==original[key],('unrelated field changed',key)
            print(('LIVE' if args.live_address else 'SIMULATED')+': check/follow, last-value hold, takeover and unrelated fields PASS')
            if args.live_address:
                discovered=request('/api/state')['ocr']['targets']
                for target in ('shot','home_score','away_score','home_fouls','away_fouls','period'):
                    if not discovered[target]['can_follow']:continue
                    request('/api/ocr/follow',{'target':target})
                    values=[]
                    for _ in range(20):
                        sample=request('/api/state');values.append(sample[target])
                        assert sample['ocr']['targets'][target]['following'] and not sample['ocr']['targets']['main']['following']
                        time.sleep(.2)
                    held=request('/api/ocr/manual',{'target':target})[target];time.sleep(.5)
                    assert request('/api/state')[target]==held
                    print('LIVE '+target+': follow/mixed manual match/takeover',json.dumps({'samples':20,'first':values[0],'last':values[-1],'distinct_values':len({json.dumps(v,sort_keys=True) for v in values})}),flush=True)
            if not args.live_address:
                from ocr_mapping_checks import verify_mappings
                verify_mappings(request,wait_for,fixture,entered)
                from ocr_seven_checks import verify_seven
                verify_seven(request,wait_for,fixture,entered)
            if args.ui:
                from ui_ocr_checks import verify_ocr_ui
                verify_ocr_ui(base,request,wait_for,fixture,root,address)
            saved=request('/api/state')['ocr']['targets']
            game=request('/api/state')
            proc.terminate();proc.wait(timeout=5);proc=start()
            restarted=request('/api/state')
            assert restarted['ocr']['connection']=='disconnected' and not restarted['ocr']['following'] and restarted['main']['state']=='ready'
            assert restarted['ocr']['address']==address
            for target,view in restarted['ocr']['targets'].items():
                assert not view['following'] and view['field']==saved[target]['field']
            assert restarted['shot']['state']=='ready'
            for key in ('home_score','away_score','home_fouls','away_fouls','period','period_overtime'):assert restarted[key]==game[key],('restart lost value',key)
            print('OCR restart: settings retained, manual Ready, no automatic connection/follow PASS')
            if args.ui:
                from ui_ocr_checks import verify_disconnected_ui
                verify_disconnected_ui(base)
        except BaseException:
            log.flush()
            print('OCR test failed; native exit status:',proc.poll(),flush=True)
            print((Path(folder)/'server.log').read_text(errors='replace'),flush=True)
            native_log=Path(folder)/'fieldscoreboard.log'
            if native_log.exists():print(native_log.read_text(errors='replace'),flush=True)
            raise
        finally:
            proc.terminate();proc.wait(timeout=5)
source.shutdown();source.server_close()
