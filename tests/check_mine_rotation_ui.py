"""Mobile mining and wardrobe occupancy against production HTML and serializer fixtures."""
import json,copy,sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
sys.path.insert(0,str(ROOT))
import mine,profile_options
fixture=json.loads(Path('/tmp/rd-mine-fixture.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  work=copy.deepcopy(fixture['work']);shop=copy.deepcopy(fixture['shop']);user=copy.deepcopy(fixture['user']);errors=[]
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=urlparse(r.request.url).path
   if path in ('/work','/shop'):
    html=constants['WORK_PAGE_HTML' if path=='/work' else 'SHOP_PAGE_HTML'].replace('</head>','<link rel="stylesheet" href="/theme.css"></head>',1)
    return r.fulfill(content_type='text/html',body=html)
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
   if path.startswith('/assets/'):
    target=ROOT/path.lstrip('/');return r.fulfill(path=str(target)) if target.is_file() else r.fulfill(status=404,body='')
   if path=='/api/state':data={'ok':True,'state':shop}
   elif path=='/api/work/state':data={'ok':True,'state':work}
   elif path=='/api/work/mine':
    body=json.loads(r.request.post_data or '{}')
    try:
     payout,_=mine.action(user,body);work['mine']=mine.snapshot(user);data={'ok':True,'mine':work['mine'],'state':work,'awarded':payout}
    except mine.MineError as e:data={'ok':False,'error':str(e),'mine':mine.snapshot(user)}
   elif path=='/api/wardrobe':
    body=json.loads(r.request.post_data or '{}');profile_options.equip(user,body['outfit'],5,body.get('slot'));shop['active_outfit']=profile_options.active_outfit(user);shop['slot_locks']=profile_options.slot_locks(user);data={'ok':True,'state':shop}
   else:return r.fulfill(body='')
   return r.fulfill(content_type='application/json',body=json.dumps(data))
  page.route('**/*',route);page.goto('https://fixture.test/work?game=mine');page.wait_for_selector('.mine-vein')
  assert page.locator('#tabs .tab-btn:visible').count()==4
  assert page.locator('#tab-farm').is_visible();assert page.locator('.mine-vein').count()==3
  page.locator('.mine-vein').first.click();page.wait_for_timeout(250);assert user['mine_run']['strikes']==1
  assert page.locator('.mine-gas').get_attribute('aria-valuenow')!='0'
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=f'/tmp/mine-{width}.png',full_page=True)
  # Client midnight refresh must close new actions but retain cashout for an old shift.
  deadline=work['rotation']['reset_at'];work['rotation']['active']=['clicker','catch','workshop'];work['rotation']['reset_at']=deadline+86400;work['farm_market']['until']=deadline+86400
  page.evaluate('now=>{Date.now=()=>now}',(deadline+1)*1000)
  page.wait_for_timeout(2200)
  page.locator('#tab-mine').click();page.wait_for_timeout(200)
  assert page.locator('.mine-vein').count()==0;assert page.get_by_role('button',name='Поднять добычу',exact=False).count()==1
  page.goto('https://fixture.test/shop?wardrobe=1');page.wait_for_selector('.fitting-controls select')
  assert page.locator('select[data-slot="body"]').is_enabled()
  for slot in ('top','bottom','legs','outerwear'):assert page.locator('select[data-slot="'+slot+'"]').is_disabled()
  for slot in ('head','shoes','neck'):assert page.locator('select[data-slot="'+slot+'"]').is_enabled()
  page.locator('select[data-slot="body"]').select_option('police_male');page.wait_for_timeout(250)
  for slot in profile_options.SLOTS:
   assert page.locator('select[data-slot="'+slot+'"]').is_disabled()==(slot!='body')
  page.screenshot(path=f'/tmp/police-slots-{width}.png',full_page=True)
  page.locator('select[data-slot="body"]').select_option('');page.wait_for_timeout(200)
  assert page.locator('.slot-occupied').count()==0;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors;page.close()
 browser.close()
print('320/390/430: 3 jobs + farm, mining actions and gas, midnight cashout-only, dress/police locks and removal passed')
