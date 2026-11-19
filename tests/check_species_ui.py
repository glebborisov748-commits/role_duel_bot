"""Free species/traits setup survives navigation and submits the selected anatomy."""
import copy,json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
fixture=json.loads(Path('/tmp/rd-species-fixtures.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  for race,gender in (('robot','male'),('furry_fox','female'),('alien','female')):
   state=copy.deepcopy(fixture['states'][race]);state['onboarding']=copy.deepcopy(fixture['onboarding']);state['settings']['tour_seen']=True;state['character']['can_edit_appearance']=True
   errors=[];calls=[];page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
   page.on('pageerror',lambda e:errors.append(str(e)))
   def route(r):
    path=urlparse(r.request.url).path
    if path=='/app':return r.fulfill(content_type='text/html',body=constants['APP_PAGE_HTML'])
    if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"mock",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){},show(){},onClick(){},offClick(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){}}}};')
    if path.startswith('/assets/'):
     file=ROOT/path.lstrip('/');return r.fulfill(path=str(file)) if file.is_file() else r.fulfill(body='')
    if path.startswith('/avatars/'):return r.fulfill(path=str(ROOT/'assets/portrait_female.webp'))
    if path=='/api/app/create':
     body=r.request.post_data_json;calls.append(body);state['onboarding']=None
    if path.startswith('/api/'):
     return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state}))
    return r.fulfill(body='')
   page.route('**/*',route);page.goto('https://fixture.test/app');o=state['onboarding'];ui=state['ui']
   page.get_by_role('button',name=next(x['label'] for x in o['worlds'] if x['key']=='anime'),exact=False).click()
   page.get_by_role('button',name=ui['ob_next'],exact=True).click()
   page.get_by_role('button',name=next(x['label'] for x in o['genders'] if x['key']==gender),exact=True).click()
   page.get_by_role('button',name=ui['ob_next'],exact=True).click()
   page.locator('[data-race]').select_option(race)
   if race in ('robot','alien'):
    assert page.locator('[data-appearance=hair_color]').count()==0
    assert page.locator('[data-appearance=hair_style]').count()==0
    page.locator('[data-appearance=skin]').select_option('brown')
   else:
    page.locator('[data-appearance=hair_color]').select_option('red')
    page.locator('[data-appearance=hair_style]').select_option('curls')
   page.locator('[data-appearance=eyes]').select_option('green')
   assert page.locator('#view-onb img').count()==0
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.screenshot(path=f'/tmp/species-{race}-{width}.png',full_page=True)
   page.get_by_role('button',name=ui['ob_next'],exact=True).click()
   page.get_by_role('button',name=next(x['label'] for x in o['styles'] if x['key']=='warm'),exact=False).click()
   page.get_by_role('button',name=ui['ob_next'],exact=True).click()
   page.get_by_role('button',name=next(x['label'] for x in o['scenes'] if x['key']=='phone'),exact=False).click()
   page.get_by_role('button',name=ui['ob_done'],exact=True).click()
   page.wait_for_function('()=>!document.getElementById("view-onb").classList.contains("on")')
   assert calls and calls[0]['race']==race and calls[0]['gender']==gender
   assert calls[0]['appearance']['eyes']=='green'
   assert 'appearance_preset' not in calls[0]
   page.locator('#nav button').last.click()
   page.get_by_role('button',name=ui['look_btn'],exact=True).click()
   picker=page.locator('#sheet-box [data-race]');picker.select_option('human')
   assert page.locator('#sheet-box [data-appearance=hair_color]').count()==1
   picker.select_option('robot')
   assert page.locator('#sheet-box [data-appearance=hair_color]').count()==0
   assert 'Покрытие корпуса' in page.locator('#sheet-box').inner_text()
   picker.select_option('furry_fox')
   assert page.locator('#sheet-box [data-appearance=hair_color]').count()==1
   assert 'Окрас шерсти' in page.locator('#sheet-box').inner_text()
   assert not errors,errors
   page.close()
 browser.close()
print('320/390/430: robot, furry and alien setup, species-specific controls, free traits preserved through creation, no images generated passed')
