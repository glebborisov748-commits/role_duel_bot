"""Real mobile fitting: grouped full catalog, pagination, merged accessories and free equip."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import mannequin_catalog as catalog
BASE='http://127.0.0.1:8901'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);p=b.new_page(viewport={'width':390,'height':844});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 for gender,body in [('female','dress'),('male','casual_outfit')]:
  p.request.post(BASE+'/audit/control',data={'mode':'chat','gender':gender,'level':9});p.goto(BASE+'/shop?wardrobe=1');p.wait_for_selector('.tailor-base');p.locator('.mannequin-card .card-img').first.click();p.wait_for_selector('.wardrobe-lightbox img[src*="fitting_catalog_"]');p.locator('.wardrobe-lightbox').click();p.locator('.outfit-picker>summary').click();p.locator('select[data-slot="body"]').select_option(body)
  p.wait_for_function("suffix=>document.querySelector('.tailor-base').src.endsWith(suffix)",arg='fitting_catalog_'+gender+'_'+body+'.webp')
  p.locator('.complete-looks>summary').click();p.locator('[data-look-group="hats"]').click();assert p.locator('.complete-look').count()<=8
  card=p.locator('[data-look-key="catalog_'+gender+'_cap"]');card.click();p.locator('.preview-actions button').click();p.wait_for_selector('.fitting-detail[data-slot="head"]')
  report=p.request.get(BASE+'/audit/report').json();assert report['shop']['active_outfit']['body']==body;assert report['shop']['active_outfit']['head']=='cap';assert report['app']['stats']['bucks']==100000;assert report['photos']==1
  p.locator('.complete-looks>summary').click();p.locator('[data-look-group="accessories"]').click();before=p.locator('.complete-look').count();assert before==8;p.locator('.look-more').click();assert p.locator('.complete-look').count()>before
  p.locator('[data-look-key="catalog_'+gender+'_round_glasses"]').click();p.locator('.preview-actions button').click();p.wait_for_selector('.fitting-detail[data-slot="face"]');p.wait_for_function("()=>Array.from(document.querySelectorAll('.fitting-stage img')).every(i=>i.complete&&i.naturalWidth>0)")
  report=p.request.get(BASE+'/audit/report').json();assert report['shop']['active_outfit']['body']==body;assert report['shop']['active_outfit']['head']=='cap';assert report['shop']['active_outfit']['face']=='round_glasses';p.locator('.fitting-stage').screenshot(path='/tmp/catalog-'+gender+'-fitting.png')
  for width in (320,390,430):
   p.set_viewport_size({'width':width,'height':844});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(gender,width)
 # Decode every generated wearable, verifying actual assets rather than URL existence alone.
 urls=[catalog.image(g,k) for g,k in catalog.VIEWS]+[catalog.base(g) for g in ('female','male')]
 result=p.evaluate("""async urls=>{let bad=[];let cursor=0;await Promise.all(Array.from({length:6},async()=>{while(cursor<urls.length){let url=urls[cursor++];try{let r=await fetch(url);if(!r.ok)throw Error(r.status);let bmp=await createImageBitmap(await r.blob());if(bmp.width!==320||bmp.height!==512)bad.push(url);bmp.close();}catch(e){bad.push(url+': '+e.message);}}}));return bad;}""",urls);assert not result,result
 p.request.post(BASE+'/audit/control',data={'mode':'chat','gender':'female','inventory':{}});p.goto(BASE+'/shop?wardrobe=1');p.wait_for_selector('.complete-looks');p.locator('.complete-looks>summary').click();assert p.locator('.complete-look').count()==0;assert not errors,errors
 b.close();print('Fitting catalog browser: both genders, 320/390/430 layouts, groups/pagination, current outfit preserved on accessory equip, no bucks/photo spending and all 135 images decoded passed')
