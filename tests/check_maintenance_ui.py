"""Maintenance mini-game stays local and normal app access recovers after retry."""
import copy,json
from playwright.sync_api import sync_playwright
from ui_fixture import constants,state as initial
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);errors=[];maintenance=[True];calls=[];state=copy.deepcopy(initial)
 page.on('pageerror',lambda e:errors.append(str(e)))
 def route(r):
  path=r.request.url.split('roleduel.test')[-1].split('?')[0]
  if path=='/app':return r.fulfill(content_type='text/html',body=constants['APP_PAGE_HTML'])
  if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}}}};')
  if path.startswith('/api/'):
   calls.append(path);return r.fulfill(content_type='application/json',body=json.dumps({'ok':False,'error':'maintenance','lang':'ru'} if maintenance[0] else {'ok':True,'state':state}))
  return r.fulfill(status=404,body='')
 page.route('**/*',route);page.goto('https://roleduel.test/app');page.get_by_text('Скоро вернёмся',exact=True).wait_for()
 assert page.locator('.maintenance-grid button').count()==9
 page.wait_for_function("document.querySelectorAll('.maintenance-grid .lit').length===1")
 label=page.locator('.maintenance-grid .lit').get_attribute('aria-label');page.get_by_text('Твоя очередь · 1',exact=True).wait_for();page.get_by_role('button',name=label,exact=True).click();page.get_by_text('Запомни · уровень 2',exact=True).wait_for()
 assert all(path=='/api/app/state' for path in calls)
 page.screenshot(path='/tmp/rd-maintenance-game.png');maintenance[0]=False;page.get_by_role('button',name='Проверить готовность',exact=True).click();page.locator('#nav button').first.wait_for()
 assert page.locator('.maintenance-screen').count()==0 and not errors,errors
 browser.close();print('Local maintenance game and recovery passed',flush=True)
