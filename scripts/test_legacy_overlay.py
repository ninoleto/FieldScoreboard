"""Compare actual OBS pixels for untransformed layouts against a prior binary.

Usage: python scripts/test_legacy_overlay.py <previous-native-binary> <new-native-binary>
Uses only generated artwork and isolated configurations; requires Playwright/Pillow.
"""
from pathlib import Path
import argparse,io,json,os,shutil,socket,subprocess,tempfile,time
from urllib.request import Request,urlopen
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('previous');parser.add_argument('current');args=parser.parse_args();root=Path(__file__).resolve().parents[1]
def request(base,path,body=None,method=None):
    with urlopen(Request(base+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Content-Type':'application/json'}),timeout=5) as response:return json.load(response)
with tempfile.TemporaryDirectory() as folder,sync_playwright() as p:
    processes=[];logs=[];bases=[]
    browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'))
    try:
        for index,binary in enumerate((args.previous,args.current)):
            with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            base=f'http://127.0.0.1:{port}';bases.append(base);data=Path(folder)/str(index);data.mkdir();log=(data/'stdio.log').open('wb');logs.append(log)
            proc=subprocess.Popen([str(Path(binary).resolve()),'--config',str(data/'config.json'),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));processes.append(proc)
            for _ in range(100):
                try:request(base,'/api/state');break
                except OSError:time.sleep(.05)
        pages=[browser.new_page(viewport={'width':1920,'height':1080}) for _ in bases]
        for base,page in zip(bases,pages):page.goto(base+'/overlay');page.wait_for_selector('.stage-element')
        for scenario in ('default','fonts-alignments-dots','legacy-background'):
            if scenario=='fonts-alignments-dots':
                layout=request(bases[0],'/api/state')['layout']
                for i,(id,el) in enumerate(layout['elements'].items()):el.update(x=400+(i%3)*600,y=180+(i//3)*300,align=('left','center','right')[i%3],font=('sans','mono','serif','heavy')[i%4],bold=i%2==0)
                for base in bases:
                    for key,value in [('home_score',10),('away_score',999),('home_fouls',30),('away_fouls',4),('period_overtime',True),('home_name','LEGACY HOME'),('away_name','AWAY 123')]:request(base,'/api/game',{'field':key,'value':value})
                    request(base,'/api/layout',layout,'PUT')
            if scenario=='legacy-background':
                buf=io.BytesIO();Image.new('RGBA',(64,32),(50,120,80,80)).save(buf,format='PNG')
                for base in bases:
                    with urlopen(Request(base+'/api/background',data=buf.getvalue(),headers={'Content-Type':'image/png'})) as response:json.load(response)
                    layout=request(base,'/api/state')['layout'];layout.pop('background_transform',None);request(base,'/api/layout',layout,'PUT')
            for page in pages:page.wait_for_timeout(350)
            pictures=[Image.open(io.BytesIO(page.screenshot(omit_background=True))).convert('RGBA') for page in pages]
            assert ImageChops.difference(*pictures).getbbox(alpha_only=False) is None,scenario
            pictures[1].save(root/f'.test/legacy11-{scenario}.png')
            print('Legacy OBS pixel equality:',scenario,'PASS',flush=True)
    finally:
        browser.close()
        for proc in processes:proc.terminate();proc.wait(timeout=5)
        for log in logs:log.close()
