"""Mobile work flows: multi-turn locks, memory countdown, city routing and radio repair."""
import json,copy,sys
from pathlib import Path
from collections import deque
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
sys.path.insert(0,str(ROOT))
import workshop
initial=json.loads(Path('/tmp/rd-work.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(initial);page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);errors=[];hits=[];pipe_submissions=[];pipe_job=workshop.start({'pipe_completed':{320:0,390:3,430:6}[width]},100)
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=r.request.url.split('roleduel.test')[-1].split('?')[0]
   if path=='/work':
    hooks="""var lockState=null;window.__testWork={lock:function(){return lockState},beginLock:function(turns){hackerMode='lock';document.getElementById('hacker-mode').textContent=state.ui.hack_mode_lock;document.getElementById('hacker-wires').classList.remove('active');document.getElementById('hacker-code').style.display='none';document.getElementById('hacker-keyboard').style.display='none';startLockpick('front');lockState.stages=turns;},beginSide:function(){hackerMode='lock';document.getElementById('hacker-wires').classList.remove('active');document.getElementById('hacker-code').style.display='none';document.getElementById('hacker-keyboard').style.display='none';startLockpick('side');},wires:function(){stopLockpick();hackerMode='wires';document.getElementById('hacker-lock').classList.remove('active');document.getElementById('hacker-code').style.display='none';startHackerWires();return {colors:hackerWires,right:hackerWireRightOrder,variant:hackerWireVariant};},memory:function(){hackerMode='code';var original=Math.random;Math.random=function(){return .1};newHackerCode();Math.random=original;document.getElementById('hacker-code').style.display='flex';},run:function(){return courierRun;},steer:setCourierDirection,stop:pressCourierStopline};"""
    html=constants['WORK_PAGE_HTML'].replace('var lockState=null,lockNextSide=false;',hooks+'var lockNextSide=false;')
    return r.fulfill(content_type='text/html',body=html.replace('<head>','<head><script src="/sfx.js"></script><link rel="stylesheet" href="/theme.css">',1))
   if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
   if path.startswith('/assets/'):
    f=ROOT/path.lstrip('/');return r.fulfill(path=str(f)) if f.is_file() else r.fulfill(status=404,body='')
   if path=='/api/work/hit':hits.append(r.request.post_data_json)
   if path=='/api/work/workshop':
    body=r.request.post_data_json
    if body['action']=='start':return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'job':workshop.public(pipe_job)}))
    pipe_submissions.append(body);matched=workshop.connected(pipe_job,body['values'])
    return r.fulfill(content_type='application/json',body=json.dumps({'ok':matched,'awarded':35 if matched else 0,'state':state}))
   if path.startswith('/api/'):return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state,'awarded':110,'penalty':40}))
   return r.fulfill(status=404,body='')
  page.route('**/*',route);page.goto('https://roleduel.test/work');page.locator('#tab-clicker').click()
  turns={320:1,390:2,430:3}[width];page.evaluate('__testWork.beginLock('+str(turns)+')')
  for stage in range(turns):
   target=page.evaluate('__testWork.lock().target')
   page.locator('#lock-angle').evaluate('(n,v)=>{n.value=v;n.dispatchEvent(new Event("input"));}',target+8)
   button=page.locator('#hacker-lock-btn');button.scroll_into_view_if_needed();rect=button.bounding_box();page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.down();page.wait_for_timeout(1050);page.mouse.up()
  page.wait_for_timeout(800);assert sum(h['game']=='hacker_combo' for h in hits)==1,hits
  page.evaluate('__testWork.memory()');hint=page.locator('#hacker-mode button');assert hint.is_disabled();assert '3' in page.locator('.memory-countdown').inner_text()
  page.wait_for_timeout(3200);assert not hint.is_disabled();assert '·' in page.locator('#hacker-code').inner_text();hint.click();assert hint.is_disabled();page.wait_for_timeout(2200);assert hint.is_disabled()
  # Forcing a wrong angle must break a pick, even while the player moves it.
  page.evaluate('__testWork.beginLock(1)');bad=page.evaluate('__testWork.lock().target>0?-80:80')
  page.locator('#lock-angle').evaluate('(n,v)=>{n.value=v;n.dispatchEvent(new Event("input"));}',bad)
  button=page.locator('#hacker-lock-btn');button.scroll_into_view_if_needed();rect=button.bounding_box();page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.down();page.wait_for_timeout(1450);page.mouse.up();assert page.evaluate('__testWork.lock().health')==2
  page.evaluate('__testWork.beginSide()');page.screenshot(path=f'/tmp/rd-side-lock-{width}.png')
  pins=page.evaluate('__testWork.lock().stages')
  for _ in range(pins):
   state_now=page.evaluate('__testWork.lock()');index=state_now['order'][state_now['stage']];target=state_now['targets'][index]
   page.locator('[data-pin="'+str(index)+'"]').click();page.locator('#lock-angle').evaluate('(n,v)=>{n.value=v;n.dispatchEvent(new Event("input"));}',target)
   rect=page.locator('#hacker-lock-btn').bounding_box();page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.down();page.wait_for_timeout(650);page.mouse.up()
  page.wait_for_timeout(750);assert sum(h['game']=='hacker_combo' for h in hits)==2,hits
  # Real pointer drags connect the marked terminals.
  wires=page.evaluate('__testWork.wires()')
  for i,color in enumerate(wires['colors']):
   left=page.locator('[data-index="'+str(i)+'"]').bounding_box();right=page.locator('[data-socket="'+str(wires['right'].index(color))+'"]').bounding_box()
   page.mouse.move(left['x']+left['width']/2,left['y']+left['height']/2);page.mouse.down();page.mouse.move(right['x']+right['width']/2,right['y']+right['height']/2,steps=8);page.mouse.up()
  page.wait_for_timeout(750);assert sum(h['game']=='hacker_combo' for h in hits)==3,hits
  page.locator('#tab-courier').click();road=page.locator('#courier-road');road.scroll_into_view_if_needed();rect=road.bounding_box()
  assert not page.locator('#courier-controls').is_visible()
  assert page.locator('.city-address').count()==3
  def swipe(dx,dy):
   x=rect['x']+rect['width']/2;y=rect['y']+rect['height']/2
   page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+dx*55,y+dy*55,steps=5);page.mouse.up()
  for delivery in range(3):
   run=page.evaluate('__testWork.run()');start=(run['x'],run['y']);target=(run['target']['x'],run['target']['y']);blocks={(b['x'],b['y']) for b in run['blocks']};q=deque([(start,[])]);seen={start};path=None
   while q:
    point,steps=q.popleft()
    if point==target:path=steps;break
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
     nx,ny=point[0]+2*dx,point[1]+2*dy;mid=(point[0]+dx,point[1]+dy)
     if not(0<=nx<7 and 0<=ny<7) or mid in blocks or (nx,ny) in seen:continue
     seen.add((nx,ny));q.append(((nx,ny),steps+[(dx,dy,nx,ny)]))
   assert path is not None
   for dx,dy,nx,ny in path:
    fuel=page.evaluate('__testWork.run().fuel');swipe(dx,dy);page.wait_for_function('p=>__testWork.run().stopped&&__testWork.run().x===p[0]&&__testWork.run().y===p[1]',arg=[nx,ny]);assert page.evaluate('__testWork.run().fuel')==fuel-1
   page.wait_for_timeout(950);assert sum(h['game']=='courier' for h in hits)==delivery
   road.dblclick(position={'x':65,'y':95});page.wait_for_timeout(1150);assert sum(h['game']=='courier' for h in hits)==delivery+1,hits
  assert page.evaluate('__testWork.run().ended')
  page.screenshot(path=f'/tmp/rd-courier-puzzle-{width}.png')
  page.locator('#tab-workshop').click();page.locator('.pipe-tile').first.wait_for()
  assert page.locator('.pipe-tile').count()==pipe_job['size']**2
  page.locator('.pipe-check').click();assert not pipe_submissions
  for i,rotation in enumerate(pipe_job['solution']):
   for _ in range((rotation-pipe_job['cells'][i]['rotation'])%4):page.locator('[data-pipe="'+str(i)+'"]').click()
  assert 'Соединено' in page.locator('#pipe-result').inner_text()
  page.wait_for_timeout(250);page.screenshot(path=f'/tmp/rd-pipes-{width}.png')
  page.locator('.pipe-check').click();page.wait_for_timeout(100);assert len(pipe_submissions)==1 and workshop.connected(pipe_job,pipe_submissions[-1]['values'])
  assert not errors,errors
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.close();print('Lock, memory, city courier and pipes passed:',width,flush=True)
 browser.close()
