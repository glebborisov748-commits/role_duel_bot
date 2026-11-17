"""Generated presets remain intact: no masks, false eyes, skin patches or pasted bodies.

Selected colors are swatches and image-generation facts, not fragile photographic
pixel masks. Check all 32 hair silhouettes in the browser.
"""
import sys,base64
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import avatar_preview
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);page=browser.new_page()
 for world in ('anime','realism'):
  for gender in ('male','female'):
   for field in avatar_preview.options.choices('ru',gender):
    if field['key']!='hair_style':continue
    for item in field['items']:
     raw={'world':world,'hair_style':item['key']}
     source=avatar_preview.svg(raw,gender)
     selfsame=avatar_preview.svg({**raw,'hair_color':'silver','skin':'dark','eyes':'green','race':'elf','full':'1'},gender)
     assert source==selfsame
     uri='data:image/svg+xml;base64,'+base64.b64encode(source.encode()).decode()
     page.set_content('<img width="320" height="360" src="'+uri+'">')
     assert page.evaluate('async()=>{await document.images[0].decode();return document.images[0].naturalWidth>0}')
 print('All 32 complete presets decode without recoloring or body overlays',flush=True)
 browser.close()
