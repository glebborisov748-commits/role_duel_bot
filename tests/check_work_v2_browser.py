"""Mobile work preview, real endpoints, generated basket and temporary bonuses."""
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901';OWNER=7287815074;GUEST=5255398262
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 def control(**kwargs):return p.request.post(BASE+'/audit/control',data={'mode':'chat',**kwargs}).json()
 def go(tab):
  p.goto(BASE+'/work?game='+tab);p.wait_for_selector('#work-schedule')
 control(work_preview=True,work_fixture=True,work_release=False)
 for width in (320,390,430):
  p.set_viewport_size({'width':width,'height':844});go('mine');p.wait_for_selector('.puzzle-grid button');assert p.locator('#tab-mine').inner_text()=='🧩 Мозаика';assert p.locator('#work-sandbox-banner').is_visible();assert not p.locator('.mine-world').count();assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  for tile in p.locator('.puzzle-grid button').all():assert tile.bounding_box()['height']>=44
  if width==390:p.screenshot(path='/tmp/work-v2-mosaic.png',full_page=True)
 p.locator('.puzzle-grid button[data-index="8"]').click();p.wait_for_function("()=>document.querySelector('.casual-status').textContent.includes('Награда начислена')");assert p.locator('.casual-start').is_disabled();rewarded=p.locator('#balance').inner_text();p.reload();p.wait_for_selector('.puzzle-grid');assert p.locator('#balance').inner_text()==rewarded
 go('dig');p.wait_for_selector('.warehouse-grid button');assert '7/9' in p.locator('.casual-odds').inner_text();p.locator('.casual-crate[data-index="0"]').click();p.wait_for_function("()=>document.querySelector('.casual-collect').disabled===false");assert '6/8' in p.locator('.casual-odds').inner_text();assert p.locator('.casual-collect').bounding_box()['y']+p.locator('.casual-collect').bounding_box()['height']<=p.viewport_size['height'];p.screenshot(path='/tmp/work-v2-depot.png',full_page=True);p.locator('.casual-collect').click();p.wait_for_function("()=>document.querySelector('.casual-status').textContent.includes('Награда забрана')");assert p.locator('.casual-crate:enabled').count()==0
 report=p.request.get(BASE+'/audit/report').json();assert report['app']['stats']['bucks']==100000,report['app']['stats']
 # Freeze and wide basket are gameplay effects, not money items.
 go('catch');p.wait_for_selector('#catch-basket img[src*="work_basket_v2"]');p.evaluate('Math.random=()=>.5');before=p.locator('#catch-basket').bounding_box()['width'];hits=[];p.on('request',lambda r:hits.append(r.url) if '/api/work/hit' in r.url else None)
 def bonus(kind):
  p.evaluate("""kind=>{let f=document.querySelector('#catch-field'),b=document.querySelector('#catch-basket'),e=document.createElement('div');e.className='catch-item';e.dataset[kind]='1';e.textContent=kind==='wide'?'↔️':'❄️';e.style.cssText='left:50%;top:'+(b.offsetTop+5)+'px;animation:none;width:26px;height:26px';f.appendChild(e);} """,kind)
 bonus('wide');p.wait_for_selector('#catch-basket.wide-active');assert p.locator('#catch-basket').bounding_box()['width']>before*1.3;assert not hits
 p.evaluate("""()=>{let e=document.createElement('div');e.className='catch-item';e.dataset.probe='1';e.style.left='10%';e.style.animationDuration='10s';e.textContent='💵';document.querySelector('#catch-field').appendChild(e);} """)
 bonus('slowfall');p.wait_for_selector('#catch-field.slow-active');assert p.locator('[data-probe]').evaluate('e=>e.getAnimations()[0].playbackRate')==.45
 p.screenshot(path='/tmp/work-v2-catch.png',full_page=True)
 p.evaluate('window.originalNow=Date.now;Date.now=()=>window.originalNow()+20000');p.wait_for_function("()=>!document.querySelector('#catch-basket').classList.contains('wide-active')&&!document.querySelector('#catch-field').classList.contains('slow-active')");assert p.locator('[data-probe]').evaluate('e=>e.getAnimations()[0].playbackRate')==1
 # Public players retain the old work UI until publication.
 context=b.new_context(viewport={'width':390,'height':844});context.add_cookies([{'name':'audit_uid','value':str(GUEST),'url':BASE}]);guest=context.new_page();guest.request.post(BASE+'/audit/control',data={'uid':GUEST,'mode':'chat'});guest.goto(BASE+'/work');guest.wait_for_selector('#work-schedule');assert guest.locator('#work-sandbox-banner').is_hidden();assert guest.locator('#tab-mine').inner_text()=='Шахта';assert guest.locator('#tab-dig').inner_text()=='Раскопки'
 control(work_preview=False,work_release=True);guest.reload();guest.wait_for_selector('#work-schedule');assert guest.locator('#tab-mine').inner_text()=='🧩 Мозаика';assert guest.locator('#work-sandbox-banner').is_hidden()
 for key in ('basket','freeze','wide'):assert p.request.get(BASE+'/assets/work_'+key+'_v2.webp').status==200
 # Switching a release while a work tab is open must not leave stale controls or throw.
 p.request.post(BASE+'/audit/control',data={'mode':'mine','work_preview':False,'work_release':False});go('mine');p.wait_for_selector('.mine-world')
 control(work_preview=False,work_release=True);p.keyboard.press('ArrowRight');p.wait_for_selector('.casual-start');assert p.locator('#tab-mine').inner_text()=='🧩 Мозаика'
 control(work_preview=False,work_release=False);p.locator('.casual-start').click();p.wait_for_function("()=>document.querySelector('#tab-mine').textContent==='Шахта'");assert p.locator('.casual-grid').count()==0
 assert not errors,errors
 b.close();print('Work v2 browser: 320/390/430 puzzle layout, solve/reload payout, warehouse cashout, separate main balance, generated basket, wide/freeze pickup and expiry, private preview/public release passed')
