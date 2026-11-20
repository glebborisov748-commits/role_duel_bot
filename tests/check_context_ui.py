"""Mobile visual checks for closet clipping, avatars, four suggestions and quiet send motion."""
import copy,json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
fixture=json.loads(Path('/tmp/rd-context-fixtures.json').read_text())
release=json.loads(Path('/tmp/rd-full-release.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(fixture['state']);state['settings']['tour_seen']=True;shop=copy.deepcopy(fixture['shop']);calls=[];errors=[]
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=urlparse(r.request.url).path
   if path in ('/app','/shop'):
    key='APP_PAGE_HTML' if path=='/app' else 'SHOP_PAGE_HTML'
    return r.fulfill(content_type='text/html',body=constants[key].replace('</head>','<link rel="stylesheet" href="/theme.css"></head>',1))
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"mock",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){},show(){},onClick(){},offClick(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}},showConfirm(t,c){c(true)}}};')
   if path.startswith('/assets/'):
    f=ROOT/path.lstrip('/');assert f.is_file(),f
    return r.fulfill(path=str(f))
   if path.startswith('/avatars/'):return r.fulfill(path=str(ROOT/'assets/default_avatar_female_1.webp'))
   if path.startswith('/api/'):
    body=r.request.post_data_json if r.request.method=='POST' else {};calls.append((path,body))
    if path=='/api/app/send':state['messages'].append({'role':'user','text':body['text']});state['pending']=True
    return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':shop if path in ('/api/state','/api/wardrobe') else state}))
   return r.fulfill(body='')
  page.route('**/*',route)
  page.goto('https://fixture.test/shop?wardrobe=1');page.wait_for_selector('.fitting-stage')
  page.wait_for_function('()=>Array.from(document.querySelectorAll(".fitting-stage img")).every(x=>x.complete&&x.naturalWidth>0)')
  assert page.locator('.fitting-stage:not(.cabinet-open) .tailor-base').evaluate('e=>getComputedStyle(e).visibility')=='hidden'
  assert page.locator('.fitting-detail').count()==0
  assert page.locator('.tailor-base').get_attribute('src').endswith('complete_clean_female_0.webp')
  assert page.locator('select[data-slot="shoes"]').is_disabled()
  page.screenshot(path=f'/tmp/context-closed-{width}.png')
  page.locator('.cabinet-doors').click();page.wait_for_timeout(850)
  assert page.locator('.fitting-stage .tailor-base').evaluate('e=>getComputedStyle(e).objectFit')=='contain'
  assert page.locator('.complete-look').count()>=8
  box=page.locator('.fitting-stage').bounding_box()
  for layer in page.locator('.fitting-stage img').all():
   b=layer.bounding_box();assert abs(b['x']-box['x'])<1 and abs(b['width']-box['width'])<1
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.screenshot(path=f'/tmp/context-fitting-{width}.png')
  page.locator('.complete-looks summary').click();page.locator('.complete-look').nth(1).click();assert page.locator('.tailor-base').get_attribute('src').endswith('complete_clean_female_1.webp')
  state=copy.deepcopy(fixture['onboarding'])
  page.goto('https://fixture.test/app');page.wait_for_selector('.ob-nav .btn')
  for _ in range(2):
   page.locator('.opt:not(.locked)').first.click();page.locator('.ob-nav .btn').last.click()
  page.wait_for_selector('#onb-generate-avatar');assert page.locator('.avatar-presets,#character-template').count()==0
  assert page.locator('[data-appearance]').count()>0
  page.screenshot(path=f'/tmp/context-onboarding-{width}.png')
  state=copy.deepcopy(release['states']['super_pro']);state['settings']['tour_seen']=True;state['messages']=[];state['reply_choices']=['Привет! Чем сейчас занята?','Что тебя порадовало?','Какой фильм посмотрим?','Какую музыку включим?'];state['pending']=False
  page.goto('https://fixture.test/app');page.wait_for_selector('.rd-choice');assert page.locator('.rd-choice').count()==4
  page.locator('#input').fill('Проверяем плавное сообщение');page.locator('#send').click();page.wait_for_selector('.message-flight')
  assert page.locator('#send.send-bounce').count()==0 and page.locator('.send-sweep').count()==0
  fly=page.locator('.message-flight');colors=page.evaluate('()=>{const a=getComputedStyle(document.querySelector(".message-flight")),b=getComputedStyle(Array.from(document.querySelectorAll(".row.me .bub")).pop());return [a.backgroundImage,b.backgroundImage]}');assert colors[0]==colors[1],colors
  page.wait_for_timeout(500);assert page.locator('.send-mist').count()==8
  page.screenshot(path=f'/tmp/context-send-{width}.png');page.wait_for_timeout(2100);assert page.locator('.message-flight,.send-mist').count()==0
  assert not errors,errors
  page.close()
 browser.close()
print('320/390/430px: closed closet clipping, fixed layers, hat/neck, footwear lock, template/avatar onboarding, four suggestions and tier-colored upward mist passed')
