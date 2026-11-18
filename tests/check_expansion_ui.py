"""Mobile checks for fitting, energizer gestures, work tabs and online skin selection."""
import copy,json,sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
sys.path.insert(0,str(ROOT))
import archaeology,online_ui
fixture=json.loads(Path('/tmp/rd-billing-fixture.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(fixture['app']);shop=copy.deepcopy(fixture['shop']);work=copy.deepcopy(fixture['work']);errors=[];calls=[]
  state['stats']['energy']=65;state['stats']['energizers']=2;state['asleep']=False;state['settings']['tour_seen']=True
  shop['active_outfit']={'top':'shirt','bottom':'trousers','shoes':'heels'}
  for cat in shop['categories']:
   for item in cat['items']:
    if item['key'] in ('shirt','trousers','heels'):item['owned']=True
  diguser={'bucks':10000};archaeology.start(diguser);work['dig']=archaeology.snapshot(diguser)
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
  def route(r):
   path=urlparse(r.request.url).path
   names={'/app':'APP_PAGE_HTML','/shop':'SHOP_PAGE_HTML','/work':'WORK_PAGE_HTML','/spin':'SPIN_PAGE_HTML','/play':'PLAY_PAGE_HTML'}
   if path in names:
    html=constants[names[path]]
    if path!='/app':html=html.replace('</head>','<link rel="stylesheet" href="/theme.css"></head>',1)
    return r.fulfill(content_type='text/html',body=html)
   if path=='/online':return r.fulfill(content_type='text/html',body=online_ui.PAGE_HTML)
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}},showConfirm(t,c){c(true)}}};')
   if path.startswith('/assets/'):
    target=ROOT/path.lstrip('/');return r.fulfill(path=str(target)) if target.is_file() else r.fulfill(status=404,body='')
   if path=='/api/app/state':data={'ok':True,'state':state}
   elif path=='/api/state':data={'ok':True,'state':shop}
   elif path=='/api/app/wake':
    calls.append(path);state['stats']['energy']=143;state['stats']['energizers']=1;data={'ok':True,'state':state}
   elif path=='/api/work/state':data={'ok':True,'state':work}
   elif path=='/api/work/dig':
    body=json.loads(r.request.post_data or '{}');archaeology.action(diguser,body);work['dig']=archaeology.snapshot(diguser);data={'ok':True,'dig':work['dig'],'state':work}
   elif path.startswith('/api/work/'):
    data={'ok':True,'state':work,'awarded':10}
   elif path=='/api/online':
    data={'ok':True,'state':{'lang':'ru','bucks':1000,'bets':[0,100],'adult_allowed':True,'room':None,'skin':'male','skins':[{'key':'male','name':'Мужской образ','image':'/assets/player_avatar_anime_male_crop.webp'},{'key':'female','name':'Женский образ','image':'/assets/player_avatar_anime_female_long.webp'}]}}
   else:return r.fulfill(status=200,body='')
   return r.fulfill(content_type='application/json',body=json.dumps(data))
  page.route('**/*',route)
  page.goto('https://fixture.test/app');page.wait_for_selector('#energy-action');page.locator('#energy-action').click();page.locator('.energy-ritual').wait_for()
  assert not calls
  for _ in range(3):page.locator('.energy-ritual-can').click();page.wait_for_timeout(200)
  page.locator('.energy-ring').click();page.wait_for_timeout(750);assert len(calls)==1 and page.locator('.energy-ritual').count()==0
  page.goto('https://fixture.test/shop?wardrobe=1');page.wait_for_selector('.fitting-stage');assert page.locator('.outfit-layer').count()==3
  assert page.locator('#wardrobe-generate').count()==1
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=f'/tmp/fitting-{width}.png',full_page=True)
  page.goto('https://fixture.test/work');page.wait_for_selector('#tab-dig');page.locator('#tab-dig').click();page.wait_for_selector('.dig-cell');assert page.locator('.dig-cell').count()==25
  page.locator('.dig-cell').first.click();page.wait_for_timeout(300);assert work['dig']['run']['actions']==1
  page.screenshot(path=f'/tmp/dig-{width}.png',full_page=True)
  page.locator('#tab-courier').click();page.wait_for_timeout(400);assert page.locator('#courier-rider').is_visible()
  road=page.locator('#courier-road').bounding_box();x=road['x']+road['width']/2;y=road['y']+road['height']/2
  page.touchscreen.tap(x,y);page.wait_for_timeout(60);page.touchscreen.tap(x,y);page.wait_for_timeout(100)
  assert 'торможение' in page.locator('#courier-feedback').inner_text() or 'СТОП' in page.locator('#courier-feedback').inner_text()
  page.screenshot(path=f'/tmp/courier-{width}.png',full_page=True)
  page.goto('https://fixture.test/online');page.wait_for_selector('#online-skin');page.locator('#online-skin').select_option('female');assert 'female' in page.locator('.skin-preview').get_attribute('src')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert not errors,errors
  page.close()
 browser.close()
print('320/390/430: energy ritual charges once, fitting layers, archaeology actions, courier braking and selectable online skins passed')
