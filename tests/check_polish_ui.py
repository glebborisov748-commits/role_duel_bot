"""Actual mobile input, moving courier, trace puzzle, shop and player onboarding.

Network responses are fixtures; visual layout/motion use Chromium with the real theme.
Screenshots are kept for human inspection. This does not claim a live Telegram or
Problembo end-to-end check.
"""
import copy,json,sys
from pathlib import Path
from urllib.parse import urlparse,parse_qsl
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
sys.path.insert(0,str(ROOT))
import avatar_preview
fixtures=json.loads(Path('/tmp/rd-profile-options.json').read_text())
work=json.loads(Path('/tmp/rd-work.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(fixtures['app']);state['settings']['tour_seen']=True
  state['player']['required']=False;state['player']['value']={'gender':'male','world':'anime','name':'Мой герой','race':'human','appearance':{}}
  shop=copy.deepcopy(fixtures['shop']);calls=[];errors=[];missing=[]
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=urlparse(r.request.url).path
   if path in ('/app','/shop','/work'):
    html=constants[{'/app':'APP_PAGE_HTML','/shop':'SHOP_PAGE_HTML','/work':'WORK_PAGE_HTML'}[path]]
    if path=='/work':html=html.replace('var lockState=null,lockNextSide=false;',"var lockState=null,lockNextSide=false;window.testWork={run:function(){return courierRun},lock:function(){return lockState},side:function(){stopLockpick();document.getElementById('hacker-wires').classList.remove('active');document.getElementById('hacker-code').style.display='none';document.getElementById('hacker-keyboard').style.display='none';startLockpick('side')},wires:function(){stopLockpick();document.getElementById('hacker-lock').classList.remove('active');startHackerWires()},links:function(){return {source:wireSelected,colors:hackerWires,right:hackerWireRightOrder}},slow:function(){appendFallingItem(document.getElementById('catch-field'),50,'catch-item','🐌',{slowfall:'1'},'catch_slow')},rocket:function(){spawnRocketWithWarning(document.getElementById('catch-field'),50)}};")
    html=html.replace('<head>','<head><script src="/sfx.js"></script>',1)
    if path!='/app':html=html.replace('</head>','<link rel="stylesheet" href="/theme.css"></head>',1)
    return r.fulfill(content_type='text/html',body=html)
   if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},HapticFeedback:{impactOccurred(){},notificationOccurred(){},selectionChanged(){}}}};')
   if path=='/api/appearance-preview.svg':
    raw=dict(parse_qsl(urlparse(r.request.url).query));return r.fulfill(content_type='image/svg+xml',body=avatar_preview.svg(raw,raw.get('gender')))
   if path.startswith('/assets/'):
    f=ROOT/path.lstrip('/')
    if not f.is_file():missing.append(path);return r.fulfill(status=404,body='')
    return r.fulfill(path=str(f))
   if path.startswith('/api/'):
    body=r.request.post_data_json if r.request.method=='POST' else {};calls.append((path,body))
    if path=='/api/app/player-avatar':state['player']['required']=False;state['player']['value']=body
    if path=='/api/app/send':state['messages'].append({'id':'new','role':'user','text':body['text']})
    target=work if path.startswith('/api/work/') else shop if path in ('/api/state','/api/wardrobe','/api/buy') else state
    return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':target,'awarded':20,'penalty':0}))
   return r.fulfill(status=404,body='')
  page.route('**/*',route)
  # Shop: category geometry with the shared stylesheet loaded LAST, as in production.
  page.goto('https://roleduel.test/shop');page.wait_for_selector('#tabs button')
  assert page.locator('#tabs').get_by_text('Гардероб',exact=True).count()==0
  assert max(page.locator('#tabs button').evaluate_all('(ns)=>ns.map(n=>n.getBoundingClientRect().height)'))<=61
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.screenshot(path=f'/tmp/rd-shop-polish-{width}.png')
  page.goto('https://roleduel.test/shop?wardrobe=1');page.wait_for_selector('#wardrobe-fitting')
  assert page.locator('#tabs button').count()==1
  assert page.locator('.wardrobe-model').evaluate('(n)=>n.complete&&n.naturalWidth>0')
  page.locator('#wardrobe-fitting').select_option('bunny_outfit');page.wait_for_timeout(100)
  assert page.locator('.wardrobe-product').evaluate('(n)=>n.complete&&n.naturalWidth>0')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.screenshot(path=f'/tmp/rd-wardrobe-polish-{width}.png')
  # Mandatory player setup for a migrated account, no paid-provider API calls.
  state['player']['required']=True;state['player']['value']=None
  page.goto('https://roleduel.test/app');page.get_by_role('heading',name='Твой герой',exact=True).wait_for()
  page.locator('[data-player="gender"]').select_option('female');page.locator('[data-appearance="hair_style"]').select_option('curls')
  page.locator('[data-appearance="hair_color"]').select_option('silver');page.locator('#appearance-race').select_option('elf')
  page.screenshot(path=f'/tmp/rd-own-avatar-{width}.png')
  if width==390:
   with page.expect_file_chooser() as fc:page.get_by_role('button',name='Загрузить своё фото',exact=True).click()
   fc.value.set_files(str(ROOT/'assets/avatar_realism_female_waves.webp'))
   page.locator('.player-selfie').wait_for()
   save=page.get_by_role('button',name='Сохранить героя · бесплатно',exact=True)
   assert save.is_disabled()
   page.get_by_text('Это моё фото. Разрешаю передавать его генератору при создании фото.',exact=True).locator('input').check()
   assert page.locator('[data-appearance="hair_color"]').is_disabled()
   page.get_by_text('Сохранить внешность с фото. Отключи, чтобы применить выбранные волосы и цвета.',exact=True).locator('input').uncheck()
   assert page.locator('[data-appearance="hair_color"]').is_enabled()
  page.get_by_role('button',name='Сохранить героя · бесплатно',exact=True).click();page.wait_for_selector('#nav button')
  payload=next(body for path,body in calls if path=='/api/app/player-avatar');assert payload['gender']=='female' and payload['race']=='elf' and payload['appearance']['hair_color']=='silver'
  # Seven navigation destinations; send effects survive an immediate response.
  assert page.locator('#nav button').count()==7
  page.locator('#input').fill('Привет, давай прогуляемся');page.locator('#send').click()
  page.wait_for_timeout(90);assert page.locator('.message-flight').count()==1
  assert page.locator('#send').evaluate("n=>n.classList.contains('send-bounce')")
  page.screenshot(path=f'/tmp/rd-send-polish-{width}.png');page.wait_for_timeout(850);assert page.locator('.message-flight').count()==0
  if width==390:
   page.locator('#photo-action').click();assert '40' in page.locator('#sheet-box').inner_text()
   page.get_by_role('button',name='Поцелуй',exact=True).click();page.wait_for_timeout(100)
   assert any(path=='/api/app/photo' and body.get('pair_action')=='kiss' for path,body in calls)
   state['character']['can_avatar']=False;state['player']['can_edit']=False
   page.reload();page.locator('#nav button').nth(5).click();page.get_by_role('button',name=state['ui']['look_btn'],exact=True).click()
   page.locator('#sheet [data-appearance="hair_color"]').select_option('blue')
   assert page.get_by_role('button',name='🔒 SUPER PRO / ELITE',exact=True).is_disabled()
   assert page.locator('#sheet-box').evaluate("n=>n.classList.contains('appearance-locked')")
   page.screenshot(path='/tmp/rd-locked-appearance.png')
   assert not any(path=='/api/app/appearance' for path,_ in calls)
  # Courier visibly moves before any gestures. Actual swipe and double tap deliver.
  page.goto('https://roleduel.test/work');page.locator('#tab-courier').click();page.wait_for_selector('#courier-delivery')
  before=page.evaluate('testWork.run().travel');page.wait_for_timeout(400);assert page.evaluate('testWork.run().travel')>before+10
  road=page.locator('#courier-road');box=road.bounding_box()
  def swipe(dx,dy):
   x=box['x']+box['width']/2;y=box['y']+box['height']/2
   page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+dx,y+dy,steps=5);page.mouse.up()
  swipe(65,0);assert page.evaluate('testWork.run().lane')==2
  swipe(-65,0);assert page.evaluate('testWork.run().lane')==1
  swipe(0,-65);assert page.evaluate('testWork.run().speed')>1
  swipe(0,65);assert page.evaluate('testWork.run().speed')<1.1
  swipe(0,-65)
  # Keep random obstacles off the tested delivery route; do not teleport the moving marker.
  lane=page.evaluate('testWork.run().targetLane')
  page.evaluate('testWork.run().obstacles.forEach(o=>o.y=-3000)')
  while page.evaluate('testWork.run().lane')!=lane:swipe(65 if page.evaluate('testWork.run().lane')<lane else -65,0)
  page.wait_for_function('Math.abs(testWork.run().targetY-document.getElementById("courier-road").clientHeight*.78)<20',timeout=12000)
  road.dblclick();page.wait_for_function('testWork.run().delivered===1',timeout=3000)
  courier_hits=[b for path,b in calls if path=='/api/work/hit' and b['game']=='courier'];assert len(courier_hits)==1 and courier_hits[0]['hit_id']
  assert page.locator('#courier-controls').is_hidden();page.screenshot(path=f'/tmp/rd-courier-polish-{width}.png')
  # A visible side pick, moving when the pin is lifted; wrong tension breaks sooner.
  page.locator('#tab-clicker').click();page.evaluate('testWork.side()');page.locator('#side-pick-tool').wait_for()
  assert page.locator('#side-pick-tool').bounding_box()['width']>100
  page.locator('#lock-angle').evaluate('(n)=>{n.value=100;n.dispatchEvent(new Event("input"));}')
  assert page.locator('#side-pick-tool').evaluate('n=>parseFloat(n.style.bottom)')>50
  page.evaluate('testWork.lock().selected=testWork.lock().order[0]');button=page.locator('#hacker-lock-btn');button.scroll_into_view_if_needed();b=button.bounding_box();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2);page.mouse.down();page.wait_for_timeout(700);page.mouse.up();assert page.evaluate('testWork.lock().health')<3
  page.screenshot(path=f'/tmp/rd-lock-polish-{width}.png')
  page.evaluate('testWork.wires()');page.wait_for_timeout(100)
  assert page.locator('.hacker-wire-end').evaluate_all('(ns)=>ns.every(n=>!n.textContent.trim())')
  left=page.locator('.hacker-wire-end').first.bounding_box();right=page.locator('.hacker-wire-socket').first.bounding_box()
  assert right['x']-left['x']>width*.5
  assert page.locator('#hacker-wires-svg path').count()>=6
  assert page.locator('#hacker-wires-svg path').first.evaluate('n=>n.getBBox().width')>width*.4
  count=page.locator('.hacker-wire-end').count()
  for i in range(count):
   data=page.evaluate('testWork.links()');idx=data['right'].index(data['colors'][data['source']]);page.locator('.hacker-wire-socket').nth(idx).click();page.wait_for_timeout(65)
  page.wait_for_timeout(100);assert any(path=='/api/work/hit' and b['game']=='hacker_combo' for path,b in calls)
  page.evaluate('testWork.wires()');page.wait_for_timeout(100);page.screenshot(path=f'/tmp/rd-wire-polish-{width}.png')
  # Falling sprites remain actual emoji at fixed dimensions; rockets are not giant bombs.
  page.locator('#tab-catch').click();page.evaluate('testWork.rocket()');page.wait_for_timeout(550)
  assert '🧺' in page.locator('#catch-basket').inner_text()
  assert page.locator('#catch-field .sprite').count()==0
  assert page.locator('.rocket').evaluate('n=>n.textContent')=='🚀'
  assert page.locator('.rocket').evaluate('n=>n.offsetWidth')<=37
  page.screenshot(path=f'/tmp/rd-catch-polish-{width}.png')
  assert not errors,errors
  assert not missing,missing
  page.close();print('Mobile player, shop, send, moving courier, lock, wires, emoji catch passed:',width,flush=True)
 browser.close()
