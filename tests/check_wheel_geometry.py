"""Wheel rim remains circular and centered on narrow mobile viewports."""
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
state=json.loads(Path('/tmp/rd-spin-fixture.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=urlparse(r.request.url).path
   if path=='/spin':return r.fulfill(content_type='text/html',body=constants['SPIN_PAGE_HTML'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},BackButton:{hide(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){}}}};')
   if path=='/api/spin/state':return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state}))
   if path.startswith('/assets/'):
    file=ROOT/path.lstrip('/');return r.fulfill(path=str(file)) if file.is_file() else r.fulfill(status=404,body='')
   return r.fulfill(body='')
  page.route('**/*',route);page.goto('https://fixture.test/spin');page.wait_for_selector('.prize-row')
  wheel=page.locator('#wheel').bounding_box();rim=page.locator('#wheel-rim').bounding_box()
  assert abs(wheel['width']-wheel['height'])<1,(width,wheel)
  assert abs(wheel['x']+wheel['width']/2-rim['x']-rim['width']/2)<1,(width,wheel,rim)
  assert abs(wheel['y']+wheel['height']/2-rim['y']-rim['height']/2)<1,(width,wheel,rim)
  assert page.locator('.prize-row').count()==12
  assert '%' not in page.locator('#prize-list-items').inner_text()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  page.screenshot(path=f'/tmp/wheel-rim-{width}.png',full_page=True);page.close()
 browser.close()
print('320/390/430: circular centered wheel, 12 prizes, no displayed odds or overflow passed')
