"""Real local city UI: mobile geometry, controls, traffic, tips and staged rollout."""
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901';GUEST=5255398262
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844});errors=[];posts=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:posts.append(r.url) if '/api/work/courier' in r.url else None)
 def reset(**kw):return p.request.post(BASE+'/audit/control',data={'mode':'chat','work_preview':True,'courier_release':False,**kw}).json()
 def go():p.goto(BASE+'/work?game=courier');p.wait_for_selector('#courier-road.courier-city')
 for width in (320,390,430):
  reset();p.set_viewport_size({'width':width,'height':844});go();p.wait_for_selector('#city-begin');assert p.locator('#courier-road').get_attribute('data-lanes')=='4';assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
  p.locator('#city-begin').click();p.wait_for_selector('#courier-rider');p.wait_for_timeout(400)
  geometry=p.evaluate("()=>{let r=document.querySelector('#courier-road').getBoundingClientRect(),b=document.querySelector('#courier-rider').getBoundingClientRect();return {ratio:(b.y+b.height/2-r.y)/r.height,pseudo:getComputedStyle(document.querySelector('#courier-road'),'::before').display}}")
  assert abs(geometry['ratio']-.78)<.02,(width,geometry);assert geometry['pseudo']=='none';assert p.locator('#city-left').is_disabled()
  for control in p.locator('#courier-controls button').all():assert control.bounding_box()['height']>=44
  if width==390:p.screenshot(path='/tmp/city-mobile.png',full_page=True)
 p.locator('#city-stop').click();p.wait_for_function("()=>Number(document.querySelector('#city-speed').textContent)>=6");p.locator('#city-right').click();p.wait_for_function("()=>document.querySelector('#courier-rider').style.left==='58%'");p.wait_for_timeout(300);p.keyboard.press('ArrowRight');p.wait_for_function("()=>document.querySelector('#courier-rider').style.left==='74%'")
 p.locator('#city-stop').click();p.wait_for_function("()=>document.querySelector('#city-left').disabled");assert p.locator('#city-right').is_disabled()
 # Product test controls invoke server-guarded scenarios, no direct client money mutation.
 p.locator('#city-test-controls summary').click();p.locator('[data-scenario="green"]').click();p.wait_for_selector('.city-intersection[data-light="green"]');car=p.locator('.city-cross-car.first');left=car.get_attribute('style');p.wait_for_timeout(350);assert car.get_attribute('style')==left
 p.locator('[data-scenario="red"]').click();p.wait_for_selector('.city-intersection[data-light="red"]');left=p.locator('.city-cross-car.first').get_attribute('style');p.wait_for_timeout(350);assert p.locator('.city-cross-car.first').get_attribute('style')!=left
 p.locator('[data-scenario="pedestrians"]').click();p.wait_for_selector('.city-crossing[data-walking="true"]',timeout=7000);assert p.locator('.city-ped:visible').count()==2
 p.locator('[data-scenario="empty_crossing"]').click();p.wait_for_selector('.city-crossing[data-walking="false"]');assert p.locator('.city-ped:visible').count()==0;assert p.locator('.city-stopline').count()==0
 # A deterministic local fixture parks the private courier for a once-only tip check.
 reset(city_fixture='parked_tip');go();p.wait_for_selector('.city-tip-burst',timeout=5000);assert '800' in p.locator('.city-tip-burst').inner_text();assert '440' in p.locator('#city-notice').inner_text();p.screenshot(path='/tmp/city-tips.png',full_page=True)
 report=p.request.get(BASE+'/audit/report').json();assert report['app']['stats']['bucks']==100000;assert report['work']['bucks']==11240
 p.goto(BASE+'/work?game=farm');p.wait_for_selector('#game-farm');p.wait_for_timeout(400);before=len(posts);p.wait_for_timeout(750);assert len(posts)==before
 context=b.new_context(viewport={'width':390,'height':844});context.add_cookies([{'name':'audit_uid','value':str(GUEST),'url':BASE}]);guest=context.new_page();guest.on('pageerror',lambda e:errors.append(str(e)));guest.request.post(BASE+'/audit/control',data={'uid':GUEST,'mode':'chat','work_preview':False,'courier_release':False});guest.goto(BASE+'/work?game=courier');guest.wait_for_selector('.courier-avenue');assert not guest.locator('#city-test-controls').count()
 reset(courier_release=True);guest.reload();guest.wait_for_selector('#city-begin');assert not guest.locator('#city-test-controls').count()
 reset(courier_release=False);guest.locator('#city-begin').click();guest.wait_for_selector('.courier-avenue');assert not errors,errors
 for key in ('car_blue','car_gray','ped_blue','ped_rust','house_brick','house_shop','house_office','house_plum','light_red','light_amber','light_green','zebra','limit_30','limit_40','limit_50','stopline','barrier','puddle','bump','pothole'):assert p.request.get(BASE+'/assets/city_'+key+'.webp').status==200,key
 b.close();print('City browser: 320/390/430 geometry, four lanes and proper rider position, responsive movement/brake controls, red/green cars, pedestrians/empty crossing, once-only tip UI, sandbox wallet, pause and staged public rollback passed')
