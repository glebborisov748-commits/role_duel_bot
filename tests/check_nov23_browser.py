"""Real localhost route and two-account flow regressions. Uses serve_repair_audit.py only."""
import os
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901';OWNER=7287815074;GUEST=5255398262
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 def make(uid,width=390):
  ctx=browser.new_context(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);ctx.add_cookies([dict(name='audit_uid',value=str(uid),url=BASE)]);p=ctx.new_page();p.errors=[];p.on('pageerror',lambda e:p.errors.append(str(e)));return p
 host=make(OWNER);guest=make(GUEST)
 def reset(p,**kw):
  uid=int(p.context.cookies(BASE)[0]['value']);r=p.request.post(BASE+'/audit/control',data=dict(uid=uid,**kw));assert r.ok,r.text();return r.json()
 def api(p,path,body=None):
  return p.evaluate('''async ({path,body})=>{let r=await fetch(path,{method:body?'POST':'GET',headers:{'X-Telegram-Init-Data':Telegram.WebApp.initData,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});return await r.json()}''',dict(path=path,body=body))
 for game in (() if os.getenv('SKIP_ROOMS') else ('rps18','rps','connect4','chess','dice')):
  reset(host,mode='chat');reset(guest,mode='chat');host.goto(BASE+'/online?game='+game);guest.goto(BASE+'/online?game=dice');host.wait_for_selector('#game-select');guest.wait_for_selector('#game-select')
  if game=='rps18':host.locator('#adult').check();assert host.locator('#adult').bounding_box()['width']>=25
  host.get_by_role('button',name='Позвать друга',exact=True).click();host.wait_for_selector('.code');code=host.locator('.code').inner_text();assert len(code)==8,code
  guest.locator('#invite').fill('https://t.me/repair_audit_bot?start=match_'+code);guest.get_by_role('button',name='Посмотреть комнату',exact=True).click();guest.wait_for_selector('#join-confirm')
  if game=='rps18':
   guest.locator('#join-confirm').click();assert guest.locator('#arena').is_hidden();guest.locator('#adult').check()
  guest.locator('#join-confirm').click();guest.wait_for_selector('#arena:not([hidden])');host.wait_for_function("()=>!document.querySelector('#arena').innerText.includes('Ждём второго игрока')")
  assert api(host,'/api/online',{'action':'state'})['state']['room']['status']=='playing',game
  if game.startswith('rps'):
   host.get_by_role('button',name='🪨',exact=True).click();guest.get_by_role('button',name='✌️',exact=True).click();host.wait_for_function("()=>document.querySelector('#arena').innerText.includes('1 : 0')")
  state=api(host,'/api/online',{'action':'state'})['state'];assert api(host,'/api/online',{'action':'leave','room':state['room']['id']})['ok']
  assert not host.errors and not guest.errors,(host.errors,guest.errors)
  print('Two-account room join and play:',game,flush=True)
 # Dead account gets a usable screen; ordinary mutations remain blocked.
 reset(host,mode='chat',dead=True,stock=1);host.goto(BASE+'/app');host.wait_for_selector('.death-panel');assert not api(host,'/api/app/send',{'text':'Не должно отправляться'})['ok']
 before=api(host,'/api/app/state')['state'];host.get_by_role('button',name='Использовать дефибриллятор из запаса',exact=True).click();host.wait_for_selector('#composer',state='visible');after=api(host,'/api/app/state')['state'];assert not after['dead'] and after['messages']==before['messages'];assert after['stats']['water']==100
 reset(host,mode='chat',dead=True,stock=0);host.reload();host.wait_for_selector('.death-panel');assert api(host,'/api/app/invoice',{'payload':'defibrillator','method':'stars'})['ok'];assert not api(host,'/api/app/invoice',{'payload':'photo_3','method':'stars'})['ok'];host.get_by_role('button',name='Начать с новым персонажем',exact=True).click();host.wait_for_selector('.ob-nav')
 print('Recovery, preserved history and clean new-character flow passed',flush=True)
 for width in (320,390,430):
  page=make(OWNER,width);reset(page,mode='chat',level=8,inventory={});page.goto(BASE+'/shop?wardrobe=1');page.wait_for_selector('.fitting-stage');assert page.locator('.cabinet-doors:visible').count()==0;assert page.locator('.tailor-base').get_attribute('src').endswith('nov23_starter_female.webp');assert page.locator('.complete-look').count()==0
  page.get_by_role('button',name='🔞 Игрушки 18+',exact=True).click();assert '9' in page.locator('#items').inner_text();assert page.locator('.preview-only').count()==0
  reset(page,mode='chat',level=9);page.reload();page.wait_for_selector('#tabs');page.get_by_role('button',name='🔞 Игрушки 18+',exact=True).click();assert page.locator('.preview-only').count()==7;assert page.locator('.preview-only .buy-btn').count()==0
  reset(page,mode='chat');page.goto(BASE+'/app');page.wait_for_selector('#h-bucks');page.locator('#h-bucks').click();page.wait_for_selector('#sheet.on');assert 'бакс' in page.locator('#sheet-box').inner_text().lower();page.locator('#sheet').evaluate("e=>e.classList.remove('on')")
  page.locator('#energy-action').click();page.wait_for_selector('.energy-can-wrap');can=page.locator('.energy-can-wrap').bounding_box();assert abs(can['height']-can['width'])<2,can;assert can['y']>150
  assert page.locator('.energy-gesture').evaluate("e=>Number(getComputedStyle(e).opacity)")==0
  # The full mixed-action tutorial and gesture sequence live in check_coaching_browser.py.
  page.wait_for_timeout(2800);assert page.locator('.energy-guide.visible').count()==0
  page.locator('.energy-close').click();page.wait_for_selector('.energy-ritual',state='detached')
  reset(page,mode='chat',tour=True);page.reload();page.wait_for_selector('.rd-tour');assert page.locator('.tour-next').count()==1;assert page.locator('.rd-tour-panel').bounding_box()['height']<=210
  page.locator('.tour-close').click();page.wait_for_selector('.rd-tour',state='detached');assert api(page,'/api/app/state')['state']['settings']['tour_seen']
  assert not page.errors,page.errors;page.screenshot(path=f'/tmp/nov23-profile-{width}.png');page.context.close();print('Mobile wardrobe, gates, energy gesture and action tutorial passed:',width,flush=True)
 # Chief-only preview must show the mini-game and allow leaving via command/backend flag.
 reset(host,mode='chat',maintenance_preview=True);host.goto(BASE+'/app');host.wait_for_selector('.maintenance-grid');host.locator('.maintenance-grid button').first.click();reset(host,mode='chat',maintenance_preview=False);host.get_by_role('button',name='Проверить готовность',exact=True).click();host.wait_for_selector('#composer',state='visible')
 print('Maintenance preview mini-game passed',flush=True)
 browser.close()
