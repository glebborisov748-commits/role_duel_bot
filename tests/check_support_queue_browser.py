"""Two real signed Mini App sessions: live queue positions and unsent draft retention."""
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901';FREE=5255398251;PAID=5255398252
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);errors=[]
 def session(uid,tier):
  c=b.new_context(viewport={'width':390,'height':844});c.add_cookies([{'name':'audit_uid','value':str(uid),'url':BASE}]);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.request.post(BASE+'/audit/control',data={'uid':uid,'mode':'chat','tier':tier});p.goto(BASE+'/app');p.wait_for_selector('#nav');p.locator('#nav [data-tab="profile"]').click();return p
 free=session(FREE,None);free.locator('#sup-text').fill('Помощь без подписки');free.locator('#sup-text').locator('..').locator('button').click();free.wait_for_function("document.querySelector('.support-status').textContent.includes('Твоя очередь: 1')")
 free.locator('#sup-text').fill('Мой незавершённый черновик')
 paid=session(PAID,'super_pro');paid.locator('#sup-text').fill('Помощь с подпиской');paid.locator('#sup-text').locator('..').locator('button').click();paid.wait_for_function("document.querySelector('.support-status').textContent.includes('Твоя очередь: 1')")
 assert 'Приоритет подписчика' in paid.locator('.support-status').inner_text()
 free.wait_for_function("document.querySelector('.support-status').textContent.includes('Твоя очередь: 2')",timeout=18000);assert free.locator('#sup-text').input_value()=='Мой незавершённый черновик'
 assert 'приоритет в очереди' in free.locator('.support-status').inner_text()
 paid.request.post(BASE+'/audit/control',data={'uid':PAID,'mode':'chat','tier':None})
 free.wait_for_function("document.querySelector('.support-status').textContent.includes('Твоя очередь: 1')",timeout=18000);assert free.locator('#sup-text').input_value()=='Мой незавершённый черновик'
 assert not errors,errors;b.close();print('Support browser: subscription priority, automatic queue updates after expiry, visible position and draft preservation passed')
