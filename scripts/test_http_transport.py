"""Regression for Windows connection-close requests with optional action bodies.

No retries: a reset, truncated JSON response or wrong status fails immediately.
"""
from pathlib import Path
import argparse,json,socket,subprocess,tempfile,time
from urllib.request import Request,urlopen
from urllib.error import HTTPError

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('binary');args=parser.parse_args();binary=Path(args.binary).resolve()
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
with tempfile.TemporaryDirectory() as folder:
    with (Path(folder)/'stdio.log').open('wb') as log:
        proc=subprocess.Popen([str(binary),'--config',str(Path(folder)/'config.json'),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:
            for _ in range(100):
                try:urlopen(base+'/api/health').close();break
                except OSError:time.sleep(.05)
            for body in (b'{}',b''):
                for _ in range(500):
                    with urlopen(Request(base+'/api/clock/main/reset',data=body,headers={'Content-Type':'application/json','Connection':'close'}),timeout=5) as response:
                        state=json.load(response);assert state['main']['state']=='ready' and len(state['ocr']['targets'])==7
                print('500 complete reset responses, connection-close body',repr(body),'PASS',flush=True)
            for _ in range(500):
                try:urlopen(Request(base+'/api/clock/main/pause',data=b'{}',headers={'Content-Type':'application/json','Connection':'close'}),timeout=5)
                except HTTPError as error:assert error.code==400 and json.load(error)['error'];continue
                raise AssertionError('Expected pause of Ready clock to be rejected')
            print('500 complete rejected action responses with optional JSON body PASS',flush=True)
        except BaseException:
            for name in ('stdio.log','fieldscoreboard.log'):
                p=Path(folder)/name
                if p.exists():print(p.read_text(errors='replace'),flush=True)
            raise
        finally:proc.terminate();proc.wait(timeout=5)
