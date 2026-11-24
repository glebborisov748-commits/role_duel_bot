"""Actual localhost APIs plus mobile browser flows; providers and Telegram are mocked."""
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (320,390,430):
  page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  def reset(mode):
   response=page.request.post(BASE+'/audit/control',data={'mode':mode});assert response.ok,response.text()
  reset('chat');page.goto(BASE+'/app');page.wait_for_selector('#input')
  for wrap in page.locator('#msgs .has-reactions').all():
   b=wrap.locator('.bub').bounding_box();r=wrap.locator('.message-reactions').bounding_box();assert r['x']<b['x']+15,(r,b)
   bottom=wrap.locator('.bub').evaluate('(e)=>{let r=document.createRange();r.selectNodeContents(e);return Array.from(r.getClientRects()).pop().bottom}');assert r['y']>=bottom-1,(r,bottom)
  page.screenshot(path=f'/tmp/repair-chat-{width}.png')
  page.locator('#input').fill('Проверяем клавиатуру');page.locator('#send').click();page.wait_for_selector('.send-flight-anchor')
  assert page.evaluate("document.activeElement.id==='input'")
  before=page.locator('.send-flight-anchor').bounding_box()['y'];page.set_viewport_size({'width':width,'height':640});page.wait_for_timeout(80)
  anchor=page.locator('.send-flight-anchor').bounding_box();field=page.locator('#input').bounding_box();assert abs(anchor['y']-field['y'])<2,(anchor,field)
  page.set_viewport_size({'width':width,'height':844});page.wait_for_timeout(80)
  assert abs(page.locator('.send-flight-anchor').bounding_box()['y']-page.locator('#input').bounding_box()['y'])<2
  page.wait_for_timeout(2200)
  reset('chat');page.goto(BASE+'/shop');page.wait_for_selector('.card-energizer')
  assert page.locator('.card-energizer .old-price').count()==4
  old=page.locator('.old-price').first;assert old.evaluate("e=>getComputedStyle(e,'::after').transform").startswith('matrix(1, 0, 0, 1'),old.evaluate("e=>getComputedStyle(e,'::after').transform")
  page.screenshot(path=f'/tmp/repair-discounts-{width}.png')
  page.get_by_role('button',name='💧 Напитки',exact=True).click();page.wait_for_selector('.card .old-price');old=page.locator('.old-price').first
  assert old.evaluate("e=>getComputedStyle(e,'::after').transform").startswith('matrix(1, 0, 0, 1')
  reset('wardrobe');page.goto(BASE+'/shop?wardrobe=1');page.wait_for_selector('.fitting-stage');page.locator('.cabinet-doors').click();page.wait_for_timeout(800)
  assert page.locator('.tailor-base').get_attribute('src').endswith('fitting_catalog_female_female_corset_skirt.webp')
  assert page.locator('.fitting-detail[data-slot="body"]').count()==0
  page.wait_for_function('()=>document.querySelector(".tailor-base").naturalWidth>0');page.screenshot(path=f'/tmp/repair-wardrobe-{width}.png')
  page.locator('#wardrobe-generate').click();page.wait_for_timeout(400);assert page.request.get(BASE+'/audit/report').json()['photos']==0
  page.locator('select[data-slot="body"]').select_option('female_bikini');page.wait_for_timeout(350)
  assert page.locator('.tailor-base').get_attribute('src').endswith('fitting_catalog_female_female_bikini.webp')
  page.screenshot(path=f'/tmp/repair-bikini-{width}.png')
  page.locator('.complete-looks summary').click();assert page.locator('.complete-look').count()>50
  # Buying clothes changes only inventory/balance; no popup or character reply.
  before=page.request.get(BASE+'/audit/report').json();card=page.locator('.card').filter(has=page.get_by_text('Шапка бини',exact=True));card.get_by_role('button',name='Купить',exact=True).click();page.wait_for_timeout(300)
  after=page.request.get(BASE+'/audit/report').json();assert before['history']==after['history'] and before['sent_messages']==after['sent_messages'];assert page.evaluate('window.__popups.length')==0
  page.screenshot(path=f'/tmp/repair-cards-{width}.png')
  reset('chat');page.goto(BASE+'/app');page.wait_for_selector('#energy-action');energy_before=page.request.get(BASE+'/audit/report').json()['app']['stats']['energizers'];page.locator('#energy-action').click();page.wait_for_selector('.energy-gesture')
  can=page.locator('.energy-can-wrap').bounding_box();assert can['height']<=351 and can['y']>150,can
  assert page.locator('.energy-gesture').evaluate('im=>im.complete&&im.naturalWidth>0')
  drag=page.locator('.energy-ritual-can').bounding_box();cx=drag['x']+drag['width']/2;cy=drag['y']+drag['height']/2;page.mouse.move(cx,cy);page.mouse.down()
  for i in range(12):page.mouse.move(cx+(50 if i%2==0 else -50),cy,steps=3);page.wait_for_timeout(350)
  page.mouse.up()
  ring=page.locator('.energy-ring');assert ring.is_enabled();r=ring.bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2
  page.mouse.move(x,y);page.mouse.down();page.mouse.move(x,y-80,steps=6);page.wait_for_timeout(350);assert page.locator('.can-opened').count()==0
  page.wait_for_timeout(650);assert page.locator('.can-opened').count()==1;page.screenshot(path=f'/tmp/repair-can-{width}.png');page.mouse.up();page.wait_for_timeout(1100)
  assert page.request.get(BASE+'/audit/report').json()['app']['stats']['energizers']==energy_before-1
  reset('mine');page.goto(BASE+'/work?game=mine');page.wait_for_selector('.mine-world-canvas');page.wait_for_timeout(400)
  assert page.locator('.maze-cell').count()==0
  dial=page.locator('.mine-aim');dial.click(position={'x':80,'y':44});page.wait_for_timeout(350)
  angle=page.request.get(BASE+'/audit/report').json()['work']['mine']['run']['maze']['angle'];assert angle<15 or angle>345,angle
  page.locator('.pad-right').click();page.wait_for_timeout(350)
  current=page.request.get(BASE+'/audit/report').json()['work']['mine']['run'];assert (current['maze']['x'],current['maze']['y'])==(2,1),current['maze']
  page.get_by_role('button',name='Добывать Уголь',exact=False).click();page.wait_for_timeout(300)
  assert page.request.get(BASE+'/audit/report').json()['work']['mine']['run']['bag_value']>=18
  page.screenshot(path=f'/tmp/repair-mine-{width}.png')
  page.locator('#tab-dig').click();page.wait_for_selector('.dig-world-canvas');assert page.locator('.dig-cell').count()==0
  page.locator('#game-dig .pad-down').click();page.wait_for_timeout(350)
  dig=page.request.get(BASE+'/audit/report').json()['work']['dig']['run'];assert dig['y']==0 and dig['bag_value']>0,dig
  page.screenshot(path=f'/tmp/repair-dig-{width}.png')
  reset('onboarding');page.goto(BASE+'/app');page.wait_for_selector('.ob-nav .btn')
  for _ in range(2):page.locator('.opt:not(.locked)').first.click();page.locator('.ob-nav .btn').last.click()
  assert page.locator('.avatar-presets,#character-template').count()==0
  assert page.locator('#ob-custom').count()==1;page.locator('#ob-custom').fill('Ада Вонг из Resident Evil, сдержанная и находчивая оперативница.')
  page.locator('input.ob-in').fill('Ада');page.locator('#onb-generate-avatar').click();page.screenshot(path=f'/tmp/repair-create-{width}.png')
  page.locator('.ob-nav .btn').last.click();page.locator('.opt:not(.locked)').first.click();page.locator('.ob-nav .btn').last.click();page.locator('.opt').last.click();page.locator('.ob-nav .btn').last.click()
  page.wait_for_selector('#input');page.wait_for_timeout(700);result=page.request.get(BASE+'/audit/report').json()
  assert result['character_template']=='ada_wong' and result['avatar'] and result['photos']==0,result
  assert 'solo portrait' not in result['prompts'][-1].lower()
  assert not errors,errors
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.close();print('Passed actual APIs and mobile flows at',width,flush=True)
 browser.close()
print('Discounts, keyboard anchoring, left reactions, all body outfits, silent purchases, short ring pull, textured mine/aim/dig and SUPER PRO creation with general photo attempt passed')
