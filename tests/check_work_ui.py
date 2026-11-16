"""Browser regression: actual game motion must survive reduced-motion settings."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from ui_fixture import constants, ROOT
state = json.loads(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/rd-work.json').read_text())
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for motion in ('no-preference','reduce'):
        page = browser.new_page(viewport={'width':390,'height':844}, reduced_motion=motion)
        hits=[]; penalties=[]; errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        def route(r):
            path=r.request.url.split('roleduel.test')[-1].split('?')[0]
            if path=='/work':
                return r.fulfill(content_type='text/html',body=constants['WORK_PAGE_HTML'].replace('<head>','<head><link rel="stylesheet" href="/theme.css"><script src="/sfx.js"></script>',1))
            if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
            if path.startswith('/assets/audio/'):
                return r.fulfill(path=str(ROOT/path.lstrip('/')))
            if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
            if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
            if path=='/api/work/hit':hits.append(r.request.post_data_json)
            if path=='/api/work/penalty':penalties.append(r.request.post_data_json)
            if path.startswith('/api/'):
                return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state,'awarded':10,'lost':100,'seconds':1}))
            return r.fulfill(status=404,body='')
        page.add_init_script("const interval=window.setInterval;window.setInterval=function(f,n){return [600,900,4000].includes(n)?0:interval.apply(this,arguments);};")
        page.route('**/*',route)
        page.goto('https://roleduel.test/work')
        page.locator('#tab-catch').click()
        page.evaluate('''()=>{document.querySelectorAll('.catch-item').forEach(e=>e.remove());let e=document.createElement('div');e.className='catch-item';e.textContent='💵';e.style.left='50%';e.style.animationDuration='1s';document.querySelector('#catch-field').append(e);}''')
        page.wait_for_timeout(1300)
        assert any(x['game']=='catch' for x in hits),hits
        paid_catches=sum(x['game']=='catch' for x in hits)
        page.evaluate('''()=>{document.querySelectorAll('.catch-item').forEach(e=>e.remove());let e=document.createElement('div');e.className='catch-item';e.textContent='🧲';e.dataset.magnet='1';e.style.left='50%';e.style.animationDuration='1s';document.querySelector('#catch-field').append(e);}''')
        page.wait_for_timeout(1100)
        assert sum(x['game']=='catch' for x in hits)==paid_catches,'Powerups must not award bucks'
        page.evaluate('''()=>{window.blastPoint=null;let original=window.RDSFX.burst;window.RDSFX.burst=function(x,y){window.blastPoint={x,y};original(x,y);};document.querySelectorAll('.catch-item').forEach(e=>e.remove());let e=document.createElement('div');e.className='catch-item bomb';e.textContent='💣';e.dataset.bomb='1';e.style.left='50%';e.style.animationDuration='1s';document.querySelector('#catch-field').append(e);}''')
        page.locator('#gameover.shown').wait_for()
        blast=page.evaluate('window.blastPoint')
        basket=page.locator('#catch-basket').bounding_box()
        assert blast and abs(blast['y']-(basket['y']+basket['height']/2))<65,(blast,basket)
        assert page.locator('.rd-impact').count()==0
        assert not errors,errors
        print('Catch motion, powerups and bomb impact passed:',motion)
        page.close()
    browser.close()
