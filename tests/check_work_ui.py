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
        page.route('**/*',route)
        page.goto('https://roleduel.test/work')
        page.locator('#tab-courier').click()
        assert page.locator('#courier-rider').inner_text()=='🛵'
        # Use the actual CSS motion and collision loop, with controlled traffic.
        def traffic(cls, emoji):
            page.evaluate('''([cls,emoji])=>{document.querySelectorAll('.courier-obstacle,.courier-recipient,.courier-car').forEach(e=>e.remove());let e=document.createElement('div');e.className=cls;e.dataset.lane='1';e.textContent=emoji;e.style.top='135px';e.style.animationDuration='0.8s';e.onanimationend=()=>e.remove();document.querySelector('#courier-road').append(e);}''',[cls,emoji])
        traffic('courier-recipient','🧑')
        page.wait_for_function("document.querySelector('#courier-progress-fill').style.width !== '0%'")
        page.wait_for_timeout(250)
        assert any(x['game']=='courier' for x in hits),hits
        traffic('courier-obstacle','🚧')
        page.locator('#gameover.shown').wait_for()
        page.wait_for_timeout(250)
        assert any(x['game']=='courier' for x in penalties),penalties
        page.locator('#gameover-retry').click()
        page.locator('#tab-catch').click()
        page.evaluate('''()=>{document.querySelectorAll('.catch-item').forEach(e=>e.remove());let e=document.createElement('div');e.className='catch-item';e.textContent='💵';e.style.left='50%';e.style.animationDuration='1s';document.querySelector('#catch-field').append(e);}''')
        page.wait_for_timeout(1300)
        assert any(x['game']=='catch' for x in hits),hits
        assert not errors,errors
        print('Courier delivery and collision passed:',motion)
        page.close()
    browser.close()
