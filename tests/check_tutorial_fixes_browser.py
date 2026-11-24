"""Mobile composer separation, independent product art and equipped headwear in photo jobs."""
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 for width in (320,390,430):
  p.set_viewport_size({'width':width,'height':720});p.request.post(BASE+'/audit/control',data={'mode':'chat','level':9,'inventory':{'cap':1,'cotton_tshirt':1}});p.goto(BASE+'/app');p.wait_for_selector('#nav');p.locator('#nav [data-tab="chat"]').click();p.wait_for_selector('#input');p.locator('#input').fill(('Проверяю длинный текст сообщения. '*8));p.locator('#input').focus();p.wait_for_timeout(100)
  inp=p.locator('#input').bounding_box();hide=p.locator('#hide-keyboard').bounding_box();assert hide['y']+hide['height']<=inp['y'],(width,inp,hide)
  p.locator('#hide-keyboard').click();assert p.locator('#hide-keyboard').is_hidden()
  p.locator('#nav [data-tab="profile"]').click();assert p.locator('.hero').evaluate("e=>getComputedStyle(e,'::after').display")=='none'
  p.goto(BASE+'/shop?wardrobe=1');p.wait_for_selector('.outfit-picker');p.locator('.outfit-picker>summary').click();p.locator('select[data-slot="head"]').select_option('cap');p.wait_for_function("()=>document.querySelector('.tailor-base').src.includes('cap')");p.wait_for_function("()=>document.querySelector('.tailor-base').complete")
  report=p.request.get(BASE+'/audit/report').json();assert report['shop']['active_outfit']['head']=='cap'
  for c in report['shop']['categories']:
   if c['key'] in ('wardrobe','adult_shop'):
    assert all(not i['image'] or 'fitting_catalog_' not in i['image'] for i in c['items'])
  if width==390:p.locator('.fitting-stage').screenshot(path='/tmp/fix-cap.png')
 # The mocked provider must receive the current headwear, not an old hairstyle-only outfit.
 result=p.evaluate("async()=>{let r=await fetch('/api/app/avatar-generate',{method:'POST',headers:{'Content-Type':'application/json','X-Telegram-Init-Data':window.Telegram.WebApp.initData},body:'{}'});return r.json();}");assert result['ok'],result
 p.wait_for_function("async()=>{let r=await fetch('/audit/report');return (await r.json()).prompts.some(t=>t.includes('baseball cap')&&t.includes('entire cap visible'));}")
 assert not errors,errors;b.close();print('Tutorial fixes: mobile keyboard control outside multiline input, bounded hero effect, separate catalog product art, equipped cap retained by fitting and mocked photo prompt passed')
