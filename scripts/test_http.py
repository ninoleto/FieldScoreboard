#!/usr/bin/env python3
"""Smoke test an extracted real native Windows or Linux binary via its HTTP API.

Usage: python scripts/test_http.py /path/to/fieldscoreboard
This test uses an isolated temporary config and must not mutate user settings.
"""
import base64
import json
import platform
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

if len(sys.argv)!=2:raise SystemExit('Usage: test_http.py /path/to/fieldscoreboard')
binary=Path(sys.argv[1]).resolve()
assert binary.is_file()
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
base=f'http://127.0.0.1:{port}'
def req(route,method='GET',data=None,ctype='application/json'):
    headers={}
    if data is not None:
        data=json.dumps(data).encode() if not isinstance(data,bytes) else data
        headers['Content-Type']=ctype
    r=urllib.request.Request(base+route,data=data,headers=headers,method=method)
    with urllib.request.urlopen(r,timeout=4) as resp:
        if 'application/json' in resp.headers.get('content-type',''):return json.loads(resp.read())
        return resp.read()
with tempfile.TemporaryDirectory() as temp:
    config=Path(temp)/'config.json'
    with (Path(temp)/'server.log').open('wb') as logs:
        proc=subprocess.Popen([str(binary),'--config',str(config),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=logs,stderr=logs)
        try:
            for _ in range(45):
                if proc.poll() is not None:raise RuntimeError('server exited before responding')
                try:
                    assert req('/api/health')['version']=='0.1.0-test.17'
                    break
                except (OSError,AssertionError):time.sleep(.1)
            else:raise RuntimeError('server startup timeout')
            data=req('/api/state')
            assert data['period']==1 and data['main']['display']=='20:00' and data['shot']['display']=='24'
            assert req('/api/adjust','POST',{'field':'home_score','delta':2})['home_score']==2
            assert req('/api/game','POST',{'field':'period','value':3})['period']==3
            assert req('/api/game','POST',{'field':'period_overtime','value':True})['period_label']=='OT'
            assert req('/api/game','POST',{'field':'period_overtime','value':False})['period_label']=='3'
            assert req('/api/network-interfaces')['interfaces'] is not None
            req('/api/clock/main/set','POST',{'seconds':20,'direction':'down'})
            hidden=req('/api/game','POST',{'field':'shot_auto_hide','value':True})
            assert hidden['shot_auto_hide'] and hidden['shot_visible'] is False,hidden
            reset=req('/api/clock/shot/set','POST',{'seconds':14,'direction':'down'})
            assert reset['shot_visible'] is True,reset
            req('/api/clock/main/set','POST',{'seconds':60,'direction':'down'})
            assert req('/api/clock/main/start','POST')['main']['state']=='running'
            shot=req('/api/clock/shot/set','POST',{'seconds':14,'direction':'down'})
            assert shot['shot']['display']=='14' and shot['shot']['state']=='running'
            shot=req('/api/clock/shot/adjust','POST',{'seconds':-1})
            assert shot['shot']['display']=='13' and shot['main']['state']=='running'
            shot=req('/api/clock/shot/adjust','POST',{'seconds':1})
            assert shot['shot']['display']=='14'
            before=req('/api/state')['main']['remaining_seconds']
            shot=req('/api/clock/shot/reset','POST')
            assert shot['shot']['display']=='14' and shot['shot']['state']=='running'
            assert shot['main']['remaining_seconds'] <= before + .02
            time.sleep(.25)
            assert req('/api/clock/main/pause','POST')['main']['state']=='paused'
            shot=req('/api/clock/shot/reset','POST')
            assert shot['shot']['state']=='ready' and shot['main']['state']=='paused'
            assert req('/api/clock/shot/set','POST',{'seconds':24,'direction':'down'})['shot']['state']=='ready'
            # Combined transport resumes the existing values, never resetting them.
            before=req('/api/state')
            both=req('/api/clock/both/start','POST')
            for clock in ['main','shot']:
                assert both[clock]['state']=='running'
                assert abs(both[clock]['remaining_seconds']-before[clock]['remaining_seconds'])<.3
            time.sleep(.15)
            both=req('/api/clock/both/pause','POST')
            assert both['main']['state']=='paused' and both['shot']['state']=='paused'
            paused=req('/api/state');time.sleep(.15)
            later=req('/api/state')
            for clock in ['main','shot']:
                assert paused[clock]['remaining_seconds']==later[clock]['remaining_seconds']
            # Real server-sent event stream: first snapshot arrives without a browser.
            with urllib.request.urlopen(base+'/api/events',timeout=3) as stream:
                line=stream.readline()
                assert line.startswith(b'data: '),line
                assert json.loads(line[6:])['home_score']==2
            assert b'overlayStage' in req('/overlay')
            overlay=req('/api/overlay-state')
            assert overlay['home_score']==2 and 'token' not in overlay and 'listen' not in overlay
            with urllib.request.urlopen(base+'/api/overlay-events',timeout=3) as stream:
                line=stream.readline()
                assert line.startswith(b'data: ') and json.loads(line[6:])['home_score']==2
            old=req('/api/token')['token']
            fresh=req('/api/token/rotate','POST',b'')['token']
            assert fresh!=old and len(fresh)==64 and req('/api/token')['token']==fresh
            assert b'Field Scoreboard' in req('/')
            state=req('/api/state');state['layout']['elements']['home_score']['x']=634
            assert req('/api/layout','PUT',state['layout'])['layout']['elements']['home_score']['x']==634
            req('/api/profiles','POST',{'name':'Smoke Layout','action':'save'})
            assert 'Smoke Layout' in req('/api/profiles')['profiles']
            tiny=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+XfVgAAAAASUVORK5CYII=')
            background=req('/api/background','POST',tiny,'image/png')
            assert background['background'].endswith('.png'),background
            transform=background['background_transform']
            assert transform['mode']=='fit' and transform['width']==1080 and transform['height']==1080 and transform['x']==420 and transform['lock_aspect']
            assert req('/background/'+background['background'])==tiny
            req('/api/background','DELETE')
            assert 'background_transform' not in req('/api/state')['layout']
            background=req('/api/background?draft=1','POST',tiny,'image/png')
            layout=req('/api/state')['layout'];assert layout['background']==''
            layout['background']=background['background']
            transform.update(mode='custom',width=960,height=480,x=-25.5,y=175.25,lock_aspect=False)
            layout['background_transform']=transform
            req('/api/layout','PUT',layout)
            req('/api/profiles','POST',{'name':'Background placement','action':'save'})
            req('/api/background','DELETE')
            assert req('/api/profiles','POST',{'name':'Background placement','action':'load'})['layout']['background_transform']==transform
            assert req('/api/overlay-state')['layout']['background_transform']==transform
            c=json.loads(config.read_text());assert c['home_score']==2 and c['period']==3
            assert c['token'] and len(c['token'])==64 and c['token']==fresh
            # Restart the extracted binary with the same isolated config. Persisted
            # values survive; runtime clocks must return to Ready.
            req('/api/clock/both/start','POST')
            proc.terminate();proc.wait(timeout=5)
            proc=subprocess.Popen([str(binary),'--config',str(config),'--listen',f'127.0.0.1:{port}','--open=false'],stdout=logs,stderr=logs)
            for _ in range(60):
                try:
                    restored=req('/api/state');break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('restart timeout')
            assert restored['main']['state']=='ready' and restored['shot']['state']=='ready'
            assert restored['home_score']==2 and restored['period']==3 and restored['shot_auto_hide']
            assert restored['layout']['elements']['home_score']['x']==634
            assert restored['layout']['background_transform']==transform
            assert restored['main']['duration_seconds']==60 and restored['shot']['duration_seconds']==24
            assert req('/api/token')['token']==fresh
            assert 'Smoke Layout' in req('/api/profiles')['profiles']
            print(f'Packaged {platform.system()} HTTP smoke: PASS (startup, OT, shot auto-hide, IP discovery, independent/combined clocks, SSE, token rotation, layout, image bytes/fit/drafts/transforms, profiles, restart persistence)')
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
