"""Mobile release flows: term-preserving upgrades, portrait menu, quests, ritual and work."""
import copy,json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
fixture=json.loads(Path('/tmp/rd-full-release.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(fixture['states']['free']);state['settings']['tour_seen']=True;state['stats'].update(energy=60,energizers=2);work=copy.deepcopy(fixture['work']);calls=[];errors=[];random_mode=[.4]
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=urlparse(r.request.url).path
   if path in ('/app','/work'):
    key='APP_PAGE_HTML' if path=='/app' else 'WORK_PAGE_HTML'
    return r.fulfill(content_type='text/html',body=constants[key].replace('</head>','<link rel="stylesheet" href="/theme.css"></head>',1))
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='Math.random=()=>'+str(random_mode[0])+';window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"mock",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){},show(){},onClick(){},offClick(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}},showConfirm(t,c){c(true)}}};')
   if path.startswith('/assets/'):
    file=ROOT/path.lstrip('/');return r.fulfill(path=str(file)) if file.is_file() else r.fulfill(body='')
   if path.startswith('/avatars/'):return r.fulfill(path=str(ROOT/'assets/portrait_female.webp'))
   if path.startswith('/api/'):
    body=r.request.post_data_json if r.request.method=='POST' else {};calls.append((path,body))
    if path=='/api/app/wake':state['stats'].update(energy=138,energizers=1)
    data={'ok':True,'state':work if '/work/' in path else state,'awarded':10}
    if path=='/api/work/dig':data['dig']=work['dig']
    if path=='/api/work/mine':data['mine']=work['mine']
    return r.fulfill(content_type='application/json',body=json.dumps(data))
   return r.fulfill(body='')
  page.route('**/*',route)
  for tier in ('free','pro','super_pro','elite'):
   state=copy.deepcopy(fixture['states'][tier]);state['settings']['tour_seen']=True
   page.goto('https://fixture.test/app');page.locator('#nav button').last.click()
   page.get_by_role('button',name='💎 Премиум-магазин',exact=True).click()
   box=page.locator('#sheet-box');assert box.locator('.photo-pack').count()==3
   assert [x.split('/')[-1] for x in box.locator('.photo-pack img').evaluate_all('(xs)=>xs.map(x=>x.src)')]==['photo_pack_3.webp','photo_pack_8.webp','photo_pack_20.webp']
   page.wait_for_function('()=>Array.from(document.querySelectorAll(".photo-pack img")).every(im=>im.complete&&im.naturalWidth>0)')
   if tier=='free':page.screenshot(path=f'/tmp/release-premium-{width}.png')
   assert box.locator('.rd-sub-terms').count()==(3 if tier=='free' else 0)
   if tier in ('pro','super_pro'):assert ('Улучшить до ELITE' if tier=='super_pro' else 'Улучшить до SUPER PRO') in box.inner_text()
   assert 'Разбудить персонажа' not in box.inner_text() and 'Дефибриллятор' not in box.inner_text() and 'Сцена · 15' not in box.inner_text()
   page.get_by_role('button',name='Назад в профиль',exact=True).click()
   page.get_by_role('button',name='Изменить аватарку',exact=True).click()
   assert page.locator('#sheet-box #generate-avatar').count()==1
   page.locator('#sheet').click(position={'x':2,'y':2})
  # Locked missions remain within the daily quest card.
  state=copy.deepcopy(fixture['states']['free']);state['settings']['tour_seen']=True;state['stats'].update(energy=60,energizers=2)
  state['quests']['locked']=True;state['quests']['channel']={'title':'Открой задания: подпишись на канал','url':'https://t.me/duel_dev_channel'}
  page.goto('https://fixture.test/app');page.locator('#nav button').last.click()
  assert page.locator('.rd-quests .channel-mission').count()==1
  assert page.locator('.quest-locked button:disabled').count()==len(state['quests']['items'])
  page.locator('#nav button').first.click();page.locator('#energy-action').click()
  can=page.locator('.energy-ritual-can');box=can.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
  page.mouse.move(x,y);page.mouse.down()
  for i in range(12):page.mouse.move(x+(45 if i%2==0 else -45),y,steps=3);page.wait_for_timeout(340)
  page.mouse.up();ring=page.locator('.energy-ring');assert ring.is_enabled()
  ring.click();assert not any(path=='/api/app/wake' for path,_ in calls)
  box=ring.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
  page.mouse.move(x,y);page.mouse.down();page.mouse.move(x,y-95,steps=8);page.wait_for_timeout(350)
  assert page.locator('.can-opened').count()==0
  page.wait_for_timeout(650);assert page.locator('.can-opened').count()==1
  assert page.locator('.energy-can-open').evaluate('im=>im.complete&&im.naturalWidth>0')
  assert page.locator('.energy-ritual .btn.ghost').count()==0
  page.screenshot(path=f'/tmp/release-open-can-{width}.png')
  page.mouse.up();page.wait_for_timeout(1000)
  assert sum(path=='/api/app/wake' for path,_ in calls)==1
  page.goto('https://fixture.test/work?game=mine');page.wait_for_selector('.mine-world-canvas');assert page.locator('#sound-toggle').is_hidden()
  assert page.locator('.mine-world-canvas').count()==1 and page.locator('.mine-aim').count()==1
  page.screenshot(path=f'/tmp/release-maze-{width}.png')
  page.locator('#tab-dig').click();page.wait_for_selector('.dig-world-canvas')
  assert page.locator('.dig-world-canvas').count()==1 and page.locator('#game-dig .work-dpad').count()==1
  page.screenshot(path=f'/tmp/release-dig-{width}.png')
  page.goto('https://fixture.test/work?game=clicker');page.wait_for_selector('.hacker-wire-end')
  for _ in range(4):
   inlet=page.locator('.hacker-wire-end:not(.connected)').first;shape=inlet.inner_text();out=page.locator('.hacker-wire-socket').filter(has_text=shape).first
   a=inlet.bounding_box();b=out.bounding_box();page.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2);page.mouse.down();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2,steps=12);page.mouse.up();page.wait_for_timeout(100)
  assert any(path=='/api/work/hit' and body.get('game')=='hacker_combo' for path,body in calls)
  random_mode[0]=.9;page.goto('https://fixture.test/work?game=clicker');page.wait_for_selector('.wire-obstacle')
  assert page.locator('.wire-obstacle').count()==3
  for _ in range(3):page.locator('.wire-obstacle').first.click()
  assert page.locator('.wire-obstacle').count()==0
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors;page.close()
 browser.close()
print('320/390/430: active upgrade offers, new packs, pencil avatar, locked quests, 2.2s resistant opening, maze, side-view excavation, shape-wire dragging and removable cable blockers passed')
