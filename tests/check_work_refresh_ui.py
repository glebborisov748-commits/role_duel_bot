"""Actual frame loop collisions, gestures, delivery and front-facing lock."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
state=json.loads(Path('/tmp/rd-work.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);errors=[];hits=[];penalties=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=r.request.url.split('roleduel.test')[-1].split('?')[0]
   if path=='/work':
    html=constants['WORK_PAGE_HTML'].replace('var lockState=null;',"var lockState=null;window.__testWork={lock:function(){return lockState},beginLock:function(){hackerMode='lock';document.getElementById('hacker-mode').textContent=state.ui.hack_mode_lock;document.getElementById('hacker-wires').classList.remove('active');document.getElementById('hacker-code').style.display='none';document.getElementById('hacker-keyboard').style.display='none';startLockpick();},run:function(){return courierRun;},spawn:function(type){courierRun.objects.forEach(function(o){o.node.remove()});courierRun.objects=[];courierRun.spawnTime=-1000;courierRun.spawned=type==='delivery'?1:0;spawnCourierTraffic();var o=courierRun.objects[0];o.lane=courierRun.lane;o.node.style.left=(20+o.lane*30)+'%';o.y=document.getElementById('courier-road').clientHeight-98;}};")
    return r.fulfill(content_type='text/html',body=html.replace('<head>','<head><script src="/sfx.js"></script><link rel="stylesheet" href="/theme.css">',1))
   if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
   if path.startswith('/assets/'):
    f=ROOT/path.lstrip('/');return r.fulfill(path=str(f)) if f.is_file() else r.fulfill(status=404,body='')
   if path=='/api/work/hit':hits.append(r.request.post_data_json)
   if path=='/api/work/penalty':penalties.append(r.request.post_data_json)
   if path.startswith('/api/'):return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state,'awarded':110,'penalty':40}))
   return r.fulfill(status=404,body='')
  page.route('**/*',route);page.goto('https://roleduel.test/work');page.locator('#tab-clicker').click();page.evaluate('__testWork.beginLock()')
  page.screenshot(path=f'/tmp/rd-lock-front-{width}.png')
  target=page.evaluate('__testWork.lock().target')
  page.locator('#lock-angle').evaluate('(n,v)=>{n.value=v;n.dispatchEvent(new Event("input"));}',target+8)
  button=page.locator('#hacker-lock-btn');button.scroll_into_view_if_needed();rect=button.bounding_box();page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.down();page.wait_for_timeout(1100);page.mouse.up()
  page.wait_for_timeout(250);assert any(h['game']=='hacker_combo' for h in hits),hits
  page.locator('#tab-courier').click();page.evaluate('__testWork.run().spawnTime=-1000')
  road=page.locator('#courier-road');road.scroll_into_view_if_needed();rect=road.bounding_box()
  def swipe(dx,dy):
   x=rect['x']+rect['width']/2;y=rect['y']+rect['height']/2
   page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+dx,y+dy,steps=6);page.mouse.up()
  swipe(65,0);assert page.evaluate('__testWork.run().lane')==2
  swipe(0,-65);assert page.evaluate('__testWork.run().speed')==3
  swipe(0,65);assert page.evaluate('__testWork.run().speed')==2
  road.dblclick(position={'x':70,'y':100});assert page.evaluate('__testWork.run().stopped')
  page.evaluate('__testWork.spawn("delivery")');page.wait_for_timeout(700)
  assert sum(h['game']=='courier' for h in hits)==1,hits
  page.screenshot(path=f'/tmp/rd-courier-vertical-{width}.png')
  road.dblclick(position={'x':70,'y':100});page.evaluate('__testWork.spawn("obstacle")');page.locator('#gameover.shown').wait_for()
  assert sum(x['game']=='courier' for x in penalties)==1
  assert not errors,errors
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.close();print('Vertical courier and front lock passed:',width,flush=True)
 browser.close()
