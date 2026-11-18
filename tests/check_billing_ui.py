"""Mobile visual smoke test against actual serializer fixtures and embedded production HTML."""
import copy,json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
fixture=json.loads(Path('/tmp/rd-billing-fixture.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(fixture['app']);state['messages']=[{'id':'a','role':'assistant','text':'Привет! Как твой день?','user_reaction':'💖','reaction_animated':True},{'id':'p','role':'assistant','text':'Фото','photo':'/assets/wardrobe_model_anime_female.webp'}];state['settings']['tour_seen']=True;errors=[]
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=urlparse(r.request.url).path
   if path=='/app':return r.fulfill(content_type='text/html',body=constants['APP_PAGE_HTML'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
   if path.startswith('/assets/'):
    target=ROOT/path.lstrip('/');return r.fulfill(path=str(target)) if target.is_file() else r.fulfill(status=404,body='')
   if path=='/api/app/state':return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state}))
   return r.fulfill(status=200,body='')
  page.route('**/*',route);page.goto('https://fixture.test/app');page.wait_for_selector('#nav');page.wait_for_timeout(300)
  assert page.locator('.message-reactions').count()==1
  pill=page.locator('.message-reactions button').bounding_box();assert pill['height']<=32
  page.locator('.bub img').last.click();assert page.locator('.photo-viewer').count()==1;page.locator('.photo-viewer button').click()
  page.locator('#nav button[data-tab="profile"]').click() if page.locator('#nav button[data-tab="profile"]').count() else page.locator('#nav button').last.click()
  page.get_by_role('button',name='Подписки и покупки',exact=True).click();page.wait_for_timeout(200)
  assert page.locator('.photo-pack').count()==3
  assert page.locator('#sheet-box').inner_text().find('Без подписки')<0
  assert page.locator('#sheet-box button[data-payload="subscribe_pro_week"]').count()==1
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  page.screenshot(path=f'/tmp/billing-{width}.png',full_page=True);page.close()
 browser.close()
print('Mobile 320/390/430: profile purchases, prices, photo packs, reaction capsule, photo viewer, no JS errors/overflow passed')
