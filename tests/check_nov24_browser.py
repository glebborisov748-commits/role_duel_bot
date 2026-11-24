"""Mobile layout, real shop purchase and support API; delayed-provider visual sequence."""
import time,re
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 p=b.new_page(viewport={'width':390,'height':844});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.request.post(BASE+'/audit/control',data={'mode':'chat'})
 for width in (320,390,430):
  p.set_viewport_size({'width':width,'height':844});p.goto(BASE+'/shop');p.wait_for_selector('#exchange-clock');p.wait_for_selector('.save-badge')
  assert p.locator('#exchange-feature').bounding_box()['y'] < p.locator('#tabs').bounding_box()['y']
  for badge in p.locator('.save-badge').all():
   assert '%' in badge.inner_text()
   assert badge.evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
   assert badge.evaluate('(e)=>e.getBoundingClientRect().right<=e.closest(".card").getBoundingClientRect().right')
  assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  first=p.locator('#exchange-clock').inner_text();p.wait_for_timeout(1150);second=p.locator('#exchange-clock').inner_text();assert first!=second
  assert re.fullmatch(r'\d{2}:\d{2}:\d{2}',second)
  p.locator('#tabs .tab').nth(1).click();third=p.locator('#exchange-clock').inner_text();assert third<=second,(first,second,third)
  p.locator('#tabs .tab').first.click()
  if width==390:p.screenshot(path='/tmp/nov24-shop.png',full_page=True)
 before=p.request.get(BASE+'/audit/report').json()['shop'];reset=before['exchange_clock']['reset_at']
 p.locator('#exchange-feature button').click();p.wait_for_timeout(350)
 after=p.request.get(BASE+'/audit/report').json()['shop'];offer=next(c for c in after['categories'] if c['key']=='exchange')['items'][0]
 assert offer['ready_in'];assert abs(after['exchange_clock']['reset_at']-reset)<2
 p.goto(BASE+'/shop?wardrobe=1');p.wait_for_selector('.tailor-base');assert not p.locator('#exchange-feature').is_visible()
 # Whole previews loaded; no external model call.
 p.locator('.complete-looks summary').click();assert p.locator('.complete-look img[src*="nov24_"]').count()>=5
 p.locator('.complete-look img[src*="nov24_"]').first.wait_for();p.screenshot(path='/tmp/nov24-looks.png',full_page=True)
 # Creation fields omit accessories, wardrobe remains independently available.
 data=p.request.post(BASE+'/audit/control',data={'mode':'onboarding'}).json()['state']['onboarding']
 assert all(f['key']!='accessory' for fields in data['appearance_fields_by_gender'].values() for f in fields)
 p.request.post(BASE+'/audit/control',data={'mode':'chat'})
 p.goto(BASE+'/app');p.wait_for_selector('#nav');p.locator('#nav [data-tab="profile"]').click();p.locator('#sup-text').fill('Нужна помощь с проверкой магазина')
 p.locator('#sup-text').locator('..').locator('button').click();p.wait_for_function("()=>document.querySelector('.support-status').textContent.includes('Твоя очередь: 1')")
 p.wait_for_timeout(1700);assert 'Твоя очередь: 1' in p.locator('.support-status').inner_text()
 # Maintenance has a single heading and a playable memory game.
 p.request.post(BASE+'/audit/control',data={'mode':'chat','maintenance_preview':True});p.goto(BASE+'/app');p.wait_for_selector('.maintenance-grid button');assert p.locator('#full').inner_text().count('Технические работы')==1;p.screenshot(path='/tmp/nov24-maintenance.png')
 p.request.post(BASE+'/audit/control',data={'mode':'chat','maintenance_preview':False});p.goto(BASE+'/app');p.wait_for_selector('#nav');p.locator('#nav [data-tab="chat"]').click();p.wait_for_selector('#input')
 pending={};started=[0]
 def send(route):
  response=route.fetch();data=response.json();pending.update(data['state']);pending['pending']=True;started[0]=time.monotonic();data['state']=pending;route.fulfill(response=response,json=data)
 def poll(route):
  response=route.fetch();data=response.json()
  if pending and time.monotonic()-started[0]<3.0:data['state']=pending
  route.fulfill(response=response,json=data)
 p.route('**/api/app/send',send);p.route('**/api/app/state',poll)
 p.evaluate("window.replyEntrances=[];new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{if(n.nodeType===1&&n.classList.contains('reply-enter'))window.replyEntrances.push(n.dataset.messageId);}))).observe(document.querySelector('#msgs'),{childList:true});")
 p.locator('#input').fill('Проверяю новую анимацию ответа');p.locator('#send').click();p.wait_for_selector('.send-flight-anchor')
 p.wait_for_selector('.read-eye.closed');assert p.locator('.typing-bub').count()==0
 p.wait_for_timeout(430);assert p.locator('.read-eye.closed').count()==1;assert p.locator('.typing-bub').count()==0
 assert 'в сети' in p.locator('#h-status').inner_text()
 p.wait_for_selector('.read-eye.open',timeout=1800);p.wait_for_selector('.typing-bub',timeout=1800);assert p.locator('.read-eye.open').count()==1
 p.wait_for_timeout(700);assert p.locator('.read-eye.open').count()==1;assert p.locator('.read-eye svg').evaluate('(e)=>getComputedStyle(e).animationName')=='read-blink'
 p.wait_for_function('window.replyEntrances.length===1',timeout=5000)
 p.wait_for_timeout(1700);assert p.locator('.reply-enter').count()==0;assert p.locator('.read-eye').count()==0;assert p.evaluate('window.replyEntrances.length')==1;assert p.locator('.send-flight-anchor').count()==0
 assert not errors,errors
 b.close();print('Nov24 browser: 320/390/430 layouts, countdown/purchase, generated looks, creation fields, support queue, maintenance, eye/typing/entrance passed')
