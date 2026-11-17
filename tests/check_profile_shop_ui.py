"""Mobile wardrobe purchase, content checkboxes, race editing and creation."""
import json,copy
from pathlib import Path
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
fixtures=json.loads(Path('/tmp/rd-profile-options.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(fixtures['app']);state['settings']['tour_seen']=True;shop=copy.deepcopy(fixtures['shop']);shop['bucks']=1000;calls=[];errors=[]
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   from urllib.parse import urlparse,parse_qsl
   path=urlparse(r.request.url).path
   if path in ('/app','/shop'):
    html=constants['APP_PAGE_HTML' if path=='/app' else 'SHOP_PAGE_HTML']
    return r.fulfill(content_type='text/html',body=html.replace('<head>','<head><script src="/sfx.js"></script><link rel="stylesheet" href="/theme.css">',1))
   if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},showPopup(){},HapticFeedback:{impactOccurred(){},notificationOccurred(){},selectionChanged(){}}}};')
   if path.startswith('/assets/'):
    f=ROOT/path.lstrip('/');return r.fulfill(path=str(f)) if f.is_file() else r.fulfill(status=404,body='')
   if path=='/api/appearance-preview.svg':
    import sys
    sys.path.insert(0,str(ROOT));import avatar_preview
    raw=dict(parse_qsl(urlparse(r.request.url).query));return r.fulfill(content_type='image/svg+xml',body=avatar_preview.svg(raw,raw.get('gender')))
   if path.startswith('/api/'):
    body=r.request.post_data_json if r.request.method=='POST' else {};calls.append((path,body))
    if path=='/api/wardrobe':
     shop['wardrobe_outfit']=body['outfit']
    if path=='/api/buy':
     assert body['category']=='wardrobe' and body['key']=='stockings'
     shop['bucks']-=200;next(i for c in shop['categories'] for i in c['items'] if i['key']=='stockings')['owned']=True
    if path=='/api/app/settings':state['content_settings']['preferences']=body['preferences'];state['content_settings']['race']=body['race']
    if path=='/api/app/create':state['onboarding']=None
    return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':shop if path in ('/api/state','/api/buy','/api/wardrobe') else state}))
   return r.fulfill(status=404,body='')
  page.route('**/*',route);page.goto('https://roleduel.test/shop')
  page.get_by_role('button',name='Гардероб',exact=True).click();assert page.locator('#items > .card').count()==5
  assert page.locator('#items .buy-btn:disabled').count()==4
  assert page.locator('#tabs button').first.inner_text()=='Гардероб'
  assert page.locator('#tabs button').evaluate_all('(nodes)=>new Set(nodes.map(n=>Math.round(n.getBoundingClientRect().top))).size')<=2
  assert page.locator('#items .card-note').count()==0
  page.locator('#items .buy-btn:not(:disabled)').click();page.wait_for_function("document.querySelectorAll('#items .buy-btn:disabled').length===5")
  assert shop['bucks']==800 and sum(path=='/api/buy' for path,_ in calls)==1
  page.locator('#wardrobe-fitting').select_option('bunny_outfit');page.locator('#wardrobe-equip').click();page.wait_for_timeout(100);assert shop['wardrobe_outfit']=='bunny_outfit'
  page.screenshot(path=f'/tmp/rd-wardrobe-{width}.png')
  page.goto('https://roleduel.test/app');page.locator('#nav button').nth(5).click();page.locator('#content-settings').click()
  assert page.locator('[data-preference]').count()==5
  assert page.locator('[data-preference="latex_style"]').is_checked()
  page.locator('[data-preference="foot_focus"]').check();page.locator('[data-preference="latex_style"]').uncheck();page.locator('#content-race').select_option('succubus')
  page.screenshot(path=f'/tmp/rd-content-settings-{width}.png');page.locator('#content-save').click();page.wait_for_timeout(100)
  page.reload();page.locator('#nav button').nth(5).click();page.locator('#content-settings').click()
  assert page.locator('[data-preference="foot_focus"]').is_checked() and not page.locator('[data-preference="latex_style"]').is_checked()
  assert page.locator('#content-race').input_value()=='succubus'
  state['onboarding']=copy.deepcopy(fixtures['onboarding']);page.reload()
  page.get_by_role('button',name=next(w['label'] for w in state['onboarding']['worlds'] if w['key']=='anime'),exact=False).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
  page.get_by_role('button',name=state['onboarding']['genders'][0]['label'],exact=True).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
  assert page.locator('#ob-race option').count()==10;page.locator('#ob-race').select_option('elf')
  page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click();page.get_by_role('button',name='Нежный',exact=False).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
  page.get_by_role('button',name='Переписка',exact=False).click();page.get_by_role('button',name=state['ui']['ob_done'],exact=True).click();page.wait_for_timeout(100)
  assert next(body for path,body in calls if path=='/api/app/create')['race']=='elf'
  if width==390:
   state['onboarding']=copy.deepcopy(fixtures['onboarding']);page.reload()
   page.get_by_role('button',name=next(w['label'] for w in state['onboarding']['worlds'] if w['key']=='realism'),exact=False).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
   page.get_by_role('button',name=state['onboarding']['genders'][1]['label'],exact=True).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
   assert page.locator('[data-appearance="species"]').count()==0
   assert page.locator('[data-appearance="hair_style"] option[value="long"]').count()==0
   assert page.locator('[data-appearance="accessory"] option[value="hairclip"]').count()==0
   page.locator('[data-appearance="hair_style"]').select_option('undercut')
   assert 'world=realism' in page.locator('.appearance-live').get_attribute('src') and 'gender=male' in page.locator('.appearance-live').get_attribute('src')
   page.screenshot(path='/tmp/rd-male-realism-builder.png')
   for _ in range(2):page.get_by_role('button',name=state['ui']['ob_back'],exact=True).click()
   page.get_by_role('button',name=next(w['label'] for w in state['onboarding']['worlds'] if w['key']=='anime'),exact=False).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
   assert 'world=anime' in page.locator('.appearance-live').get_attribute('src')
   page.screenshot(path='/tmp/rd-male-anime-builder.png')
  assert not errors,errors
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.close();print('Wardrobe, preferences and race passed:',width,flush=True)
 browser.close()
