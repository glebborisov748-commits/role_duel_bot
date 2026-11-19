"""Mobile flows for the new request, production CSS order, mocked API responses."""
import json,copy,sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
sys.path.insert(0,str(ROOT))
f=json.loads(Path('/tmp/rd-follow-fixture.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(f['app']);shop=copy.deepcopy(f['shop']);work=copy.deepcopy(f['work']);work['farm']=[{'crop':c,'emoji':e,'ready':True,'progress':1,'seconds_left':0,'watered_slots':4,'total_slots':4,'can_water':False,'payout_preview':450} for c,e in [('corn','🌽'),('tomato','🍅')]];errors=[];calls=[];missing=[]
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=urlparse(r.request.url).path
   if path in ('/app','/shop','/work'):
    html=constants[{'/app':'APP_PAGE_HTML','/shop':'SHOP_PAGE_HTML','/work':'WORK_PAGE_HTML'}[path]]
    html=html.replace('<head>','<head><script src="/sfx.js"></script>',1)
    if path!='/app':html=html.replace('</head>','<link rel="stylesheet" href="/theme.css"></head>',1)
    return r.fulfill(content_type='text/html',body=html)
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},openTelegramLink(){},showConfirm(t,c){c(true)},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
   if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path.startswith('/assets/'):
    target=ROOT/path.lstrip('/')
    if not target.is_file():missing.append(path);return r.fulfill(status=404,body='')
    return r.fulfill(path=str(target))
   if path.startswith('/avatars/'):return r.fulfill(path=str(ROOT/'assets/wardrobe_model_anime_female.webp'))
   if path=='/api/appearance-preview.svg':raise AssertionError('A library face was fetched')
   if path.startswith('/api/'):
    body=r.request.post_data_json if r.request.method=='POST' else {};calls.append((path,body))
    if path=='/api/app/task':state['quests']['channel']=None
    if path=='/api/app/send':state['messages'].append({'id':'fresh','role':'user','text':body['text']})
    if path=='/api/wardrobe':
     import profile_options
     u={'active_outfit':shop['active_outfit'],'inventory':{i['key']:1 for c in shop['categories'] for i in c['items'] if i.get('owned')}}
     profile_options.equip(u,body['outfit'],5,body.get('slot'));shop['active_outfit']=u['active_outfit']
    if path=='/api/app/create':state['onboarding']=None
    if path=='/api/app/avatar-generate':state['character']['avatar_pending']=True;state['character']['avatar_credits']=0
    data=work if path.startswith('/api/work/') else shop if path in ('/api/state','/api/wardrobe') else state
    return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':data}))
   return r.fulfill(status=404,body='')
  page.route('**/*',route)
  # Creation is descriptive choices, no own-player step or preset face.
  state['onboarding']=copy.deepcopy(f['onboarding']);page.goto('https://roleduel.test/app')
  assert page.get_by_role('heading',name='Твой герой',exact=True).count()==0
  page.get_by_role('button',name=next(w['label'] for w in state['onboarding']['worlds'] if w['key']=='anime'),exact=False).click()
  page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click();page.get_by_role('button',name=state['onboarding']['genders'][0]['label'],exact=True).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
  page.locator('[data-appearance=hair_color]').select_option('red');page.locator('[data-appearance=eyes]').select_option('green');assert page.locator('#view-onb img').count()==0
  page.screenshot(path=f'/tmp/rd-simple-creation-{width}.png')
  page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click();page.get_by_role('button',name='Нежный',exact=False).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click();page.get_by_role('button',name='Переписка',exact=False).click();page.get_by_role('button',name=state['ui']['ob_done'],exact=True).click();page.wait_for_timeout(100)
  assert next(b for path,b in calls if path=='/api/app/create')['appearance']['hair_color']=='red'
  assert page.locator('#nav button').last.inner_text().endswith('Профиль')
  assert page.locator('#nav button').nth(5).locator('img').get_attribute('src')=='/assets/nav_wardrobe.webp'
  # Reactions occupy their own row below actual message text.
  bar=page.locator('.message-reactions').first;bar.wait_for();assert bar.locator('img').get_attribute('src').split('?')[0].endswith('reaction_heart.webp')
  assert bar.evaluate('n=>getComputedStyle(n).position')=='static'
  assert bar.locator('.rd-user-react').evaluate('n=>getComputedStyle(n).backgroundColor')=='rgba(0, 0, 0, 0)'
  page.screenshot(path=f'/tmp/rd-reactions-clear-{width}.png')
  # Text remains in flight for about a second; final bubble is initially invisible.
  page.locator('#input').fill('Давай встретимся в кафе сегодня');page.locator('#send').click();page.wait_for_timeout(300)
  assert page.locator('.message-flight').count()==1
  assert page.locator('.message-arriving').last.evaluate('n=>getComputedStyle(n).opacity')=='0'
  assert page.locator('#send').evaluate('n=>getComputedStyle(n).animationName')=='send-merge'
  page.wait_for_timeout(1000);assert page.locator('.message-flight').count()==0
  assert page.locator('.message-arriving').last.evaluate('n=>Number(getComputedStyle(n).opacity)')>.95
  page.locator('#input').focus();assert page.locator('#hide-keyboard').is_visible();page.locator('#hide-keyboard').click();assert page.locator('#input').evaluate('n=>document.activeElement!==n')
  # A scroll-to-latest arrow, and no forced jump on rerender.
  state['messages']=[{'role':'assistant','id':str(i),'text':('Сообщение '+str(i)+'\n')*8} for i in range(20)]
  page.reload();page.locator('#msgs').evaluate('n=>{n.scrollTop=0;n.dispatchEvent(new Event("scroll"))}');assert page.locator('#jump-latest').is_visible();page.locator('#jump-latest').click();page.wait_for_timeout(850);assert page.locator('#jump-latest').is_hidden()
  # Context photo has no forced couple action; empty context submits no request.
  page.locator('#photo-action').click();page.wait_for_timeout(100)
  photo=next(b for path,b in calls if path=='/api/app/photo');assert 'pair_action' not in photo
  count=sum(path=='/api/app/photo' for path,_ in calls);state['messages']=[];page.reload();page.locator('#photo-action').click();page.wait_for_timeout(100);assert sum(path=='/api/app/photo' for path,_ in calls)==count
  page.get_by_role('button',name='Проверить подписку',exact=True).click();page.wait_for_timeout(80);assert state['quests']['channel'] is None
  # Profile image upload is offered free and avatar generation consumes a paid credit.
  page.locator('#nav button').last.click();assert page.get_by_role('button',name='Поставить своё фото · бесплатно',exact=True).is_visible();page.locator('#generate-avatar').click();page.wait_for_timeout(100);assert page.locator('#generate-avatar').is_disabled()
  # Wardrobe combines independent shoe, leg and body slots.
  page.goto('https://roleduel.test/shop?wardrobe=1');page.wait_for_selector('[data-slot="body"]')
  for slot,key in [('body','dress'),('legs','stockings'),('shoes','heels')]:page.locator('[data-slot="'+slot+'"]').select_option(key);page.wait_for_timeout(100)
  assert shop['active_outfit']['body']=='dress' and shop['active_outfit']['legs']=='stockings' and shop['active_outfit']['shoes']=='heels'
  page.screenshot(path=f'/tmp/rd-slots-wardrobe-{width}.png');page.get_by_role('button',name='🔞 Секс-шоп',exact=True).click();assert page.locator('#items .card').count()==len(next(c for c in shop['categories'] if c['key']=='adult_shop')['items'])
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  if width==390:
   next(c for c in shop['categories'] if c['key']=='adult_shop')['locked']=True
   page.reload();page.get_by_role('button',name='🔞 Секс-шоп',exact=True).click()
   assert page.locator('.wardrobe-lock').is_visible() and page.locator('#items .card').count()==0
  # The reported large balance + ELITE multiplier cannot displace sound.
  page.goto('https://roleduel.test/work');page.locator('#tab-catch').click();page.wait_for_timeout(100)
  box=page.locator('#topbar').bounding_box();sound=page.locator('#sound-toggle').bounding_box();title=page.locator('#title').bounding_box()
  assert abs((sound['y']+sound['height']/2)-(title['y']+title['height']/2))<5
  assert box['height']<64
  page.screenshot(path=f'/tmp/rd-fixed-work-header-{width}.png')
  page.locator('#tab-farm').click();page.wait_for_timeout(100)
  assert page.locator('#farm-plots .farm-plant .sprite').count()==2
  for n in page.locator('#farm-plots .farm-plant .sprite').all():
   assert n.evaluate('n=>n.offsetHeight')<=56 and n.evaluate('n=>n.offsetWidth')<=52
  page.screenshot(path=f'/tmp/rd-small-crops-{width}.png')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  assert not errors,errors
  assert not missing,missing
  page.close();print('Creation, transparent reactions, send motion, keyboard/scroll controls, photo context, slots and fixed work header passed:',width,flush=True)
 browser.close()
