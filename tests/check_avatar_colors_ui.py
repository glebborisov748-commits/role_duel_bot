"""Pixel-level browser check: changing iris color must not recolor surrounding skin."""
import sys,base64
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import avatar_preview
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);page=browser.new_page(viewport={'width':800,'height':360})
 for world in ('anime','realism'):
  for gender in ('male','female'):
   for style in ([r[0] for r in avatar_preview.options.MALE_HAIR] if gender=='male' else ['long','waves','bob','short','curls','ponytail','braid','pixie']):
    raw={'world':world,'hair_style':style}
    def uri(extra):return 'data:image/svg+xml;base64,'+base64.b64encode(avatar_preview.svg({**raw,**extra},gender).encode()).decode()
    page.set_content('<img id="original" width="260" height="300" src="'+uri({})+'"><img id="colored" width="260" height="300" src="'+uri({'eyes':'green'})+'">')
    result=page.evaluate('''async()=>{await Promise.all(Array.from(document.images).map(n=>n.decode()));function pixels(n){var c=document.createElement('canvas');c.width=260;c.height=300;var x=c.getContext('2d');x.drawImage(n,0,0,260,300);return x.getImageData(0,0,260,300).data;}var a=pixels(document.getElementById('original')),b=pixels(document.getElementById('colored'));var count=0,left=0,right=0,minX=260,minY=300,maxX=0,maxY=0;for(var i=0;i<a.length;i+=4)if(Math.max(Math.abs(a[i]-b[i]),Math.abs(a[i+1]-b[i+1]),Math.abs(a[i+2]-b[i+2]))>8){var x=i/4%260,y=Math.floor(i/4/260);count++;if(x<130)left++;else right++;minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}return {count,left,right,minX,minY,maxX,maxY};}''')
    assert result['left']>8 and result['right']>8,(world,gender,style,result)
    assert 88<=result['minX']<=result['maxX']<=180 and result['maxY']-result['minY']<=16,(world,gender,style,result)
    page.screenshot(path=f'/tmp/rd-eyes-{world}-{gender}-{style}.png');print('Iris-only recoloring passed:',world,gender,style,result,flush=True)
 for world in ('anime','realism'):
  raw={'world':world,'hair_style':'short'}
  def uri(extra):return 'data:image/svg+xml;base64,'+base64.b64encode(avatar_preview.svg({**raw,**extra},'male').encode()).decode()
  page.set_content('<img id="original" src="'+uri({})+'"><img id="colored" src="'+uri({'hair_color':'silver'})+'">')
  result=page.evaluate("""async()=>{await Promise.all(Array.from(document.images).map(n=>n.decode()));function px(n){var c=document.createElement('canvas');c.width=260;c.height=300;var x=c.getContext('2d');x.drawImage(n,0,0,260,300);return x.getImageData(0,0,260,300).data;}var a=px(document.getElementById('original')),b=px(document.getElementById('colored')),hair=0,skin=0;for(var y=0;y<300;y++)for(var x=0;x<260;x++){var i=(y*260+x)*4,d=Math.max(Math.abs(a[i]-b[i]),Math.abs(a[i+1]-b[i+1]),Math.abs(a[i+2]-b[i+2]));if(d>10){if(y<95)hair++;if(x>=110&&x<=150&&y>=145&&y<=270)skin++;}}return {hair,skin};}""")
  assert result['hair']>1000 and result['skin']==0,(world,result)
  print('Hair recoloring preserves face and neck:',world,result,flush=True)
 browser.close()
