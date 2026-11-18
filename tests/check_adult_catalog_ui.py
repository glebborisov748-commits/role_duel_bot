"""New shop images load for both genders on mobile; no runtime photo generation."""
import json,sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
sys.path.insert(0,str(ROOT))
from profile_options import ADULT_CATALOG_ITEMS
fixtures=json.loads(Path('/tmp/rd-adult-catalog-fixtures.json').read_text())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for gender in ('male','female'):
  for width in (320,390,430):
   state=fixtures[gender];errors=[];missing=[];api_calls=[]
   page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
   page.on('pageerror',lambda e:errors.append(str(e)))
   def route(r):
    path=urlparse(r.request.url).path
    if path=='/shop':return r.fulfill(content_type='text/html',body=constants['SHOP_PAGE_HTML'].replace('</head>','<link rel="stylesheet" href="/theme.css"></head>',1))
    if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
    if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},BackButton:{hide(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){}}}};')
    if path=='/api/state':api_calls.append(path);return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state}))
    if path.startswith('/assets/'):
     file=ROOT/path.lstrip('/')
     if file.is_file():return r.fulfill(path=str(file))
     missing.append(path);return r.fulfill(status=404,body='')
    if path.startswith('/api/'):api_calls.append(path)
    return r.fulfill(body='')
   page.route('**/*',route);page.goto('https://fixture.test/shop?wardrobe=1')
   category=next(c for c in state['categories'] if c['key']=='adult_shop')
   page.get_by_role('button',name=category['name'],exact=True).click()
   expected=[key for key,item in ADULT_CATALOG_ITEMS.items() if item['gender']==gender]
   page.wait_for_function('()=>Array.from(document.querySelectorAll("#items .card-img")).every(im=>im.complete&&im.naturalWidth>0)')
   for key in expected:
    card=page.locator('#items .card').filter(has=page.locator('.card-name').get_by_text(ADULT_CATALOG_ITEMS[key]['ru'],exact=True))
    assert card.count()==1,(gender,key)
    image=card.locator('.card-img');assert image.get_attribute('src')=='/assets/catalog_'+key+'.webp'
    assert image.evaluate('im=>im.complete&&im.naturalWidth>0')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert all(path=='/api/state' for path in api_calls),api_calls
   assert not missing,missing
   assert not errors,errors
   page.screenshot(path=f'/tmp/adult-shop-{gender}-{width}.png',full_page=False)
   page.close()
 browser.close()
print('Both genders at 320/390/430: 32 new product images, no missing files, no overflow or JS errors, no generation requests passed')
