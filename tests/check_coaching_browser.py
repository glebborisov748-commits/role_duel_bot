"""Mobile tutorial: explanations, real embedded actions, free fitting and optional final message."""
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 def at(n):p.wait_for_selector('.rd-tour[data-step="'+str(n)+'"]')
 def next(n):p.locator('.rd-tour .tour-next').click();at(n)
 def tab(name,n):p.locator('#nav [data-tab="'+name+'"]').click();at(n)
 for width in (320,390,430):
  p.set_viewport_size({'width':width,'height':844});p.request.post(BASE+'/audit/control',data={'mode':'chat','tour':True,'work_preview':True,'inventory':{'cotton_tshirt':1,'cap':1}});p.goto(BASE+'/app');at(0)
  assert p.locator('.rd-tour-panel').bounding_box()['height']<210
  assert p.locator('.rd-tour').get_attribute('data-backdrop')=='blur';assert p.locator('.tour-pointer').is_hidden()
  next(1);next(2);assert p.locator('.rd-tour').get_attribute('data-backdrop')=='dim'
  p.wait_for_timeout(80);finger=p.locator('.tour-pointer');target=p.locator('#nav [data-tab="shop"]');r=target.bounding_box();anchor=finger.evaluate('(e)=>({x:Number(e.dataset.tipX),y:Number(e.dataset.tipY)})');assert abs(anchor['x']-(r['x']+r['width']/2))<2;assert abs(anchor['y']-(r['y']+r['height']/2))<2
  tab('shop',3);shop=p.frame_locator('#view-shop iframe');shop.locator('[data-category="drinks"]').click();at(4)
  if width==390:p.screenshot(path='/tmp/coach-shop.png')
  next(5);tab('work',6);work=p.frame_locator('#view-work iframe');work.locator('#tab-farm').click();at(7);next(8);next(9);tab('wardrobe',10)
  room=p.frame_locator('#view-wardrobe iframe');room.locator('.outfit-picker>summary').click();at(11)
  fields=room.locator('.outfit-picker select');chosen=None
  for field in fields.all():
   options=field.locator('option').evaluate_all('(ns)=>ns.filter(n=>n.value&&!n.disabled).map(n=>n.value)')
   if options and field.is_enabled():chosen=field;break
  assert chosen is not None
  assert not p.locator('.rd-tour .tour-next').count();chosen.select_option(options[0]);at(12)
  p.wait_for_timeout(120);cr=p.locator('.rd-ring').bounding_box();rr=room.locator('#wardrobe-generate').bounding_box();assert abs(cr['width']-rr['width']-6)<2,(cr,rr,p.locator('.rd-ring').evaluate('(e)=>({style:e.style.cssText,transition:getComputedStyle(e).transition,viewport:visualViewport.width})'))
  if width==390:p.screenshot(path='/tmp/coach-wardrobe.png')
  next(13);tab('profile',14);next(15);next(16);p.locator('#nav [data-tab="chat"]').click()
  p.wait_for_selector('.rd-tour',state='detached');p.wait_for_function("document.querySelector('#input')&&document.querySelector('#composer').offsetHeight>0")
  report=p.request.get(BASE+'/audit/report').json();assert report['app']['settings']['tour_seen'];assert report['app']['stats']['bucks']==100000;assert len(report['history'])==2
  assert not errors,errors
 # Energy: same size ratios, separate idle can / hand hints, motion-free arrowless cursor and actual opening.
 p.request.post(BASE+'/audit/control',data={'mode':'chat'});p.goto(BASE+'/app');p.wait_for_selector('#energy-action');p.locator('#energy-action').click();p.wait_for_selector('.energy-can-wrap');box=p.locator('.energy-can-wrap').bounding_box();assert abs(box['width']-box['height'])<2;assert box['width']>p.viewport_size['width']*.88
 assert not p.locator('.energy-motion-symbol').count();assert p.locator('.energy-gesture').get_attribute('src').endswith('coach_finger.webp');assert p.locator('.energy-guide').evaluate('(e)=>Number(getComputedStyle(e).opacity)')==0
 p.wait_for_timeout(2900);assert not p.locator('.energy-guide.visible').count();p.wait_for_selector('.energy-guide.visible.swipe',timeout=4000);p.wait_for_timeout(260);assert p.locator('.energy-guide').evaluate('(e)=>Number(getComputedStyle(e).opacity)')>.8
 assert p.locator('.energy-guide-trail').evaluate('(e)=>Number(getComputedStyle(e).opacity)')>.5;p.screenshot(path='/tmp/coach-energy-swipe.png')
 x=box['x']+box['width']/2;y=box['y']+box['height']*.55;p.mouse.move(x,y);p.mouse.down();p.wait_for_timeout(300);assert p.locator('.energy-guide').evaluate('(e)=>Number(getComputedStyle(e).opacity)')<.05
 for i in range(8):p.mouse.move(x+(55 if i%2 else -55),y,steps=3);p.wait_for_timeout(340)
 p.mouse.up();p.wait_for_function("!document.querySelector('.energy-ring').disabled");p.wait_for_selector('.energy-guide.visible.pull',timeout=8000);p.wait_for_timeout(280);p.screenshot(path='/tmp/coach-energy-pull.png')
 ring=p.locator('.energy-ring').bounding_box();pointer=p.locator('.energy-guide').bounding_box();assert abs(pointer['x']+32-(ring['x']+ring['width']/2))<2
 p.mouse.move(ring['x']+ring['width']/2,ring['y']+ring['height']/2);p.mouse.down();p.mouse.move(ring['x']+ring['width']/2,ring['y']+ring['height']/2-70,steps=3);p.wait_for_timeout(430);assert p.locator('.can-opened').count()==1;p.mouse.up();p.wait_for_selector('.energy-ritual',state='detached')
 assert not errors,errors;b.close();print('Coaching browser: 320/390/430 compact mixed tutorial, embedded drinks/farm, actual free clothing equip, optional message, correct cursor anchors, faded and sequential can hints, purple swipe trail and opening passed')
