"""Mobile composer, appearance builder, subscription badges and photo status."""
import copy,json
from playwright.sync_api import sync_playwright
from ui_fixture import constants,state as initial,ROOT
import sys
sys.path.insert(0,str(ROOT))
import character_options
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  state=copy.deepcopy(initial);state['stats'].update(energy=80,energy_max=150,energizers=2);state['photo_pending']=False
  state['character'].update(appearance_fields=character_options.choices('ru'),appearance=character_options.validate({}),portrait_pending=False)
  state['subscription']={'level':None,'title':None,'until':None};state['offers']=[]
  for payload,name,price,week in [('subscribe_pro','PRO',220,75),('subscribe_super','SUPER PRO',500,170),('subscribe_elite','ELITE',1000,340)]:
   offer={'payload':payload,'title':name,'emoji':'✦','perks':['Test perk'],'stars':price,'stars_label':str(price),'rub':None};state['offers'] += [offer,{**offer,'payload':payload+'_week','stars':week,'stars_label':str(week)}]
  errors=[];calls=[];ready=[False]
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   path=r.request.url.split('roleduel.test')[-1].split('?')[0]
   if path=='/app':return r.fulfill(content_type='text/html',body=constants['APP_PAGE_HTML'].replace('<head>','<head><script src="/sfx.js"></script><link rel="stylesheet" href="/theme.css">',1))
   if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
   if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
   if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},showConfirm(t,c){c(true)},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
   if path.startswith('/assets/'):
    f=ROOT/path.lstrip('/');return r.fulfill(path=str(f)) if f.is_file() else r.fulfill(status=404,body='')
   if path.startswith('/api/'):
    body=r.request.post_data_json if r.request.method=='POST' else {};calls.append((path,body))
    if path=='/api/app/wake':state['stats']['energy']=min(150,state['stats']['energy']+78);state['stats']['energizers']-=1
    if path=='/api/app/photo':state.update(pending=True,photo_pending=True);state['stats']['energy']-=40
    if path=='/api/app/state' and ready[0] and state['pending']:
     state.update(pending=False,photo_pending=False);state['messages'].append({'id':'photo','role':'assistant','text':'📷','photo':'/assets/portrait_female.webp'})
    if path=='/api/app/settings':state['settings'].update(body)
    if path=='/api/app/create':state['onboarding']=None
    return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state}))
   return r.fulfill(status=404,body='')
  page.route('**/*',route);page.goto('https://roleduel.test/app');page.locator('#energy-action').wait_for()
  assert page.locator('#energy-action img').get_attribute('src')=='/assets/ui_energizer.webp'
  assert page.locator('#chat-photo-tools').count()==0
  page.locator('#input').fill('при');assert page.locator('.ghost-suffix').inner_text()=='вет'
  page.locator('#input').press('Tab');assert page.locator('#input').input_value()=='привет'
  page.locator('#input').fill('')
  page.locator('#energy-action').click();page.locator('.energy-drink-fx').wait_for();assert state['stats']['energy']==150
  assert page.locator('#energy-action').is_disabled()
  page.locator('#photo-action').click();page.wait_for_function("document.querySelector('#h-status').textContent.includes('отправляет фото')")
  assert any(path=='/api/app/photo' for path,_ in calls)
  assert not any(path=='/api/app/send' for path,_ in calls)
  ready[0]=True;page.locator('#msgs img[src="/assets/portrait_female.webp"]').wait_for(timeout=6000)
  page.locator('#nav button').nth(5).click();assert page.locator('#view-profile .tier').count()==3
  assert page.get_by_text('Популярно',exact=True).count()==1
  assert page.get_by_text('Выгодно',exact=True).count()==1
  assert page.locator('.monthly-best').count()==3
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.screenshot(path=f'/tmp/rd-refresh-profile-{width}.png')
  # Creation replaces four presets with validated independent appearance fields.
  state['onboarding']={'lang':'ru','worlds':[{'key':'anime','label':'Аниме'}],'genders':[{'key':'female','label':'Девушка'}],'styles':[{'key':'honest','label':'Честный','desc':'Прямой и искренний'}],'scenes':[{'key':'phone','label':'Переписка'}],'looks':[{'key':'anime_f1','world':'anime','gender':'female','label':'Base','img':'/assets/portrait_female.webp'}],'default_gender':'female','name_max':24,'can_custom':False,'appearance_fields':character_options.choices('ru'),'appearance_defaults':dict(character_options.DEFAULT)}
  page.reload();page.get_by_role('button',name='Аниме',exact=True).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
  page.get_by_role('button',name='Девушка',exact=True).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
  page.locator('select[data-appearance="hair_color"]').select_option('pink');page.locator('select[data-appearance="eyes"]').select_option('green')
  assert page.locator('select[data-appearance]').count()==8
  page.screenshot(path=f'/tmp/rd-appearance-{width}.png')
  page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click();page.get_by_role('button',name='Честный',exact=False).click();page.get_by_role('button',name=state['ui']['ob_next'],exact=True).click()
  page.get_by_role('button',name='Переписка',exact=True).click();page.get_by_role('button',name=state['ui']['ob_done'],exact=True).click()
  page.wait_for_timeout(100)
  body=next(body for path,body in calls if path=='/api/app/create');assert body['appearance']['hair_color']=='pink' and body['appearance']['eyes']=='green'
  assert not errors,errors
  page.close();print('Composer, portraits and tiers passed:',width,flush=True)
 browser.close()
