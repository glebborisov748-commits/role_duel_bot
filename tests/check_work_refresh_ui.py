"""Mobile work flows: multi-turn locks, memory countdown, trace cables and pipes."""
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
  # Follow each cable to its outlet, without numbered/color-matched terminals.
  wires=page.evaluate('__testWork.wires()')
  for i,color in enumerate(wires['colors']):
   page.locator('[data-socket="'+str(wires['right'].index(color))+'"]').click()
  page.wait_for_timeout(750);assert sum(h['game']=='hacker_combo' for h in hits)==3,hits
  # Continuous courier gestures and real-time handoff are covered in check_polish_ui.py.
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
  page.close();print('Lock, memory, trace cables and pipes passed:',width,flush=True)
 browser.close()
