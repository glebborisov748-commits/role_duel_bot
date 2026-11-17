"""Mobile work flows: multi-turn locks, memory countdown, city routing and radio repair."""
import json,copy
from pathlib import Path
from collections import deque
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
initial=json.loads(Path('/tmp/rd-work.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(initial);page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);errors=[];hits=[];radio=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=r.request.url.split('roleduel.test')[-1].split('?')[0]
   if path=='/work':
    hooks="""var lockState=null;window.__testWork={lock:function(){return lockState},beginLock:function(turns){hackerMode='lock';document.getElementById('hacker-mode').textContent=state.ui.hack_mode_lock;document.getElementById('hacker-wires').classList.remove('active');document.getElementById('hacker-code').style.display='none';document.getElementById('hacker-keyboard').style.display='none';startLockpick();lockState.stages=turns;},memory:function(){hackerMode='code';var original=Math.random;Math.random=function(){return .1};newHackerCode();Math.random=original;document.getElementById('hacker-code').style.display='flex';},run:function(){return courierRun;},steer:setCourierDirection,stop:pressCourierStopline};"""
    html=constants['WORK_PAGE_HTML'].replace('var lockState=null;',hooks)
    return r.fulfill(content_type='text/html',body=html.replace('<head>','<head><script src="/sfx.js"></script><link rel="stylesheet" href="/theme.css">',1))
   if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
   if path.startswith('/assets/'):
    f=ROOT/path.lstrip('/');return r.fulfill(path=str(f)) if f.is_file() else r.fulfill(status=404,body='')
   if path=='/api/work/hit':hits.append(r.request.post_data_json)
   if path=='/api/work/workshop':
    body=r.request.post_data_json
    if body['action']=='start':return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'job':{'id':'test-job','target':[3,6,4]}}))
    radio.append(body);matched=body['values']==[3,6,4]
    return r.fulfill(content_type='application/json',body=json.dumps({'ok':matched,'awarded':35 if matched else 0,'state':state}))
   if path.startswith('/api/'):return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state,'awarded':110,'penalty':40}))
   return r.fulfill(status=404,body='')
  page.route('**/*',route);page.goto('https://roleduel.test/work');page.locator('#tab-clicker').click()
  turns={320:1,390:2,430:3}[width];page.evaluate('__testWork.beginLock('+str(turns)+')')
  for stage in range(turns):
   target=page.evaluate('__testWork.lock().target')
   page.locator('#lock-angle').evaluate('(n,v)=>{n.value=v;n.dispatchEvent(new Event("input"));}',target+8)
   button=page.locator('#hacker-lock-btn');button.scroll_into_view_if_needed();rect=button.bounding_box();page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.down();page.wait_for_timeout(900);page.mouse.up()
  page.wait_for_timeout(800);assert sum(h['game']=='hacker_combo' for h in hits)==1,hits
  page.evaluate('__testWork.memory()');hint=page.locator('#hacker-mode button');assert hint.is_disabled();assert '3' in page.locator('.memory-countdown').inner_text()
  page.wait_for_timeout(3200);assert not hint.is_disabled();assert '·' in page.locator('#hacker-code').inner_text();hint.click();assert hint.is_disabled();page.wait_for_timeout(2200);assert hint.is_disabled()
  page.locator('#tab-courier').click();road=page.locator('#courier-road');road.scroll_into_view_if_needed();rect=road.bounding_box()
  # Swiping steers over a real finite city; stopped starts prevent accidental loss.
  x=rect['x']+rect['width']/2;y=rect['y']+rect['height']/2
  page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+55,y,steps=6);page.mouse.up();assert page.evaluate('__testWork.run().dx')==1
  road.dblclick(position={'x':70,'y':100});assert page.evaluate('__testWork.run().stopped')
  page.locator('#courier-speed').click();assert page.evaluate('__testWork.run().speed')==3
  run=page.evaluate('__testWork.run()');start=(run['x'],run['y']);target=(run['target']['x'],run['target']['y']);blocks={(b['x'],b['y']) for b in run['blocks']};q=deque([(start,[])]);seen={start};path=None
  while q:
   point,steps=q.popleft()
   if point==target:path=steps;break
   for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
    nx,ny=point[0]+dx,point[1]+dy
    if not(0<=nx<7 and 0<=ny<7) or (nx%2 and ny%2) or (nx,ny) in blocks or (nx,ny) in seen:continue
    seen.add((nx,ny));q.append(((nx,ny),steps+[(dx,dy,nx,ny)]))
  assert path is not None
  for dx,dy,nx,ny in path:
   page.evaluate('d=>__testWork.steer(d[0],d[1])',[dx,dy]);page.wait_for_function('p=>__testWork.run().x===p[0]&&__testWork.run().y===p[1]',arg=[nx,ny]);page.evaluate('__testWork.stop()')
  page.wait_for_timeout(1100);assert sum(h['game']=='courier' for h in hits)==1,hits
  page.wait_for_timeout(400);assert sum(h['game']=='courier' for h in hits)==1
  page.screenshot(path=f'/tmp/rd-city-courier-{width}.png')
  page.locator('#tab-workshop').click();page.locator('.radio-knob').first.wait_for();page.locator('.radio-check').click();page.wait_for_timeout(100);assert radio[-1]['values']==[0,0,0]
  for i,value in enumerate([3,6,4]):page.locator('[data-radio="'+str(i)+'"]').evaluate('(n,v)=>{n.value=v;n.dispatchEvent(new Event("input"));}',value)
  page.locator('.radio-check').click();page.wait_for_timeout(100);assert radio[-1]['values']==[3,6,4]
  page.screenshot(path=f'/tmp/rd-radio-{width}.png');assert not errors,errors
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.close();print('Lock, memory, city courier and radio passed:',width,flush=True)
 browser.close()
