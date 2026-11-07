from pathlib import Path
from playwright.sync_api import sync_playwright
from ui_touch_checks import choose, navigate
import requests, json, os, shutil
root=Path(__file__).resolve().parents[1]
base='http://127.0.0.1:8790'
(root/'.test').mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome'),args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda err: errors.append(str(err)))
 page.goto(base,wait_until='networkidle')
 page.wait_for_function("document.querySelector('#connected').classList.contains('ok')")
 assert page.locator('#previewStage .stage-element').count()==9
 page.locator('[data-adjust="home_score:1"]').click()
 page.wait_for_function("document.querySelector('#homeScore').textContent === '1'")
 page.locator('[data-clock-action="main:start"]').click()
 page.wait_for_function("document.querySelector('#mainState').textContent === 'RUNNING'")
 page.locator('[data-clock-action="main:pause"]').click()
 page.wait_for_function("document.querySelector('#mainState').textContent === 'PAUSED'")
 page.screenshot(path=str(root/'.test/live-desktop.png'),full_page=True)
 navigate(page,'editor')
 page.wait_for_timeout(250)
 page.screenshot(path=str(root/'.test/editor-desktop.png'),full_page=True)
 page.locator('[data-field="home_score"]').click()
 page.locator('#elementX').fill('780')
 page.locator('#elementX').blur()
 assert page.locator('#unsavedBadge').is_visible()
 page.locator('#saveLayout').click()
 page.wait_for_function('!document.querySelector("#unsavedBadge").offsetParent')
 s=requests.get(base+'/api/state').json()
 assert s['layout']['elements']['home_score']['x']==780,s['layout']['elements']['home_score']
 page.locator('#profileName').fill('Demo profile')
 page.locator('#saveProfile').click()
 page.wait_for_timeout(200)
 assert 'Demo profile' in page.locator('#profileSelect').inner_text()
 navigate(page,'control');choose(page,'homeFoulStyle','number');navigate(page,'editor')
 page.locator('#saveLayout').click()
 page.wait_for_timeout(200)
 assert requests.get(base+'/api/state').json()['layout']['foul_style_home']=='number'
 navigate(page,'setup')
 page.screenshot(path=str(root/'.test/setup-desktop.png'),full_page=True)
 assert 'http://127.0.0.1:8790/overlay' in page.locator('#overlayUrl').inner_text()
 print('desktop interaction PASS',errors)
 for w in [1920,1440,1000,500,375]:
  page.set_viewport_size({'width':w,'height':800})
  navigate(page,'editor')
  page.wait_for_timeout(150)
  scrollwidth=page.evaluate('document.documentElement.scrollWidth')
  assert scrollwidth<=w+2,(w,scrollwidth)
  page.screenshot(path=str(root/f'.test/editor-{w}px.png'),full_page=True)
  print('editor width',w,'scrollwidth',scrollwidth)
 page.close()
 overlay=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
 overlay_errors=[];overlay.on('pageerror',lambda err:overlay_errors.append(str(err)))
 overlay.goto(base+'/overlay',wait_until='domcontentloaded')
 overlay.wait_for_function("document.querySelector('[data-id=\"home_score\"]').textContent==='1'")
 print('overlay bg',overlay.evaluate('getComputedStyle(document.body).backgroundColor'))
 assert overlay.evaluate('getComputedStyle(document.body).backgroundColor')=='rgba(0, 0, 0, 0)'
 assert overlay.locator('#overlayStage .stage-element').count()==9
 box=overlay.locator('[data-id="home_score"]').bounding_box()
 assert box['x']>=700 and box['x']<=800,box
 overlay.screenshot(path=str(root/'.test/overlay-transparent.png'),omit_background=True)
 print('overlay',box,'errors',overlay_errors)
 assert not errors+overlay_errors,errors+overlay_errors
 overlay.close()
 browser.close()
print('UI checks PASS')
